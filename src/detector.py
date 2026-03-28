import re
import math
from collections import Counter
from config import (
    INDIAN_INFRA_KEYWORDS,
    ATTACK_INTENT_KEYWORDS,
    SCORING,
    SEVERITY_BANDS,
    SECTOR_KEYWORDS,
)

EMAIL_PASS_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}\s*[:|]\s*\S+")
API_KEY_RE = re.compile(r"\b(?:AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,})\b")
TOKEN_RE = re.compile(r"\b(?:token|apikey|api_key|secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?\b", re.I)
RAW_SECRET_RE = re.compile(r"\b[A-Za-z0-9_\-]{24,}\b")


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def has_high_entropy_secret(text: str, threshold: float = 3.5) -> bool:
    for m in TOKEN_RE.finditer(text):
        candidate = m.group(1)
        if len(candidate) >= 16 and shannon_entropy(candidate) >= threshold:
            return True

    for m in RAW_SECRET_RE.finditer(text):
        candidate = m.group(0)
        if shannon_entropy(candidate) >= threshold:
            return True
    return False


def classify_severity(score: int) -> str:
    for lo, hi, label in SEVERITY_BANDS:
        if lo <= score <= hi:
            return label
    return "LOW"


def classify_urgency(severity: str) -> str:
    return {
        "CRITICAL": "IMMEDIATE",
        "HIGH": "HIGH",
        "MEDIUM": "NORMAL",
        "LOW": "LOW",
    }.get(severity, "LOW")


def confidence_from_score(score: int, hits: int) -> str:
    if score >= 76 and hits >= 3:
        return "VERY_HIGH"
    if score >= 51 and hits >= 2:
        return "HIGH"
    if score >= 26:
        return "MEDIUM"
    return "LOW"


def detect_sector(text_lower: str) -> str:
    best_sector = "General"
    best_hits = 0
    for sector, words in SECTOR_KEYWORDS.items():
        hits = sum(1 for w in words if w in text_lower)
        if hits > best_hits:
            best_hits = hits
            best_sector = sector
    return best_sector


def clean_source_name(source: str) -> str:
    if not source:
        return "Unknown"

    s = source.strip().lower()

    mapping = {
        "hnrss_security": "Hacker News (Security)",
        "public forum security": "Public Forum Security",
        "credential leak monitoring": "Credential Leak Monitoring",
        "reddit cyberintel": "Reddit CyberIntel",
        "forum india cyber": "Forum India Cyber",
        "paste archive": "Paste Archive",
    }

    return mapping.get(s, source.replace("_", " ").title())


def analyze(source: str, title: str, content: str):
    text = f"{title}\n{content}"
    text_lower = text.lower()

    credential_found = bool(
        EMAIL_PASS_RE.search(text_lower)
        or API_KEY_RE.search(text)
        or has_high_entropy_secret(text)
    )
    infra_hit = any(k in text_lower for k in INDIAN_INFRA_KEYWORDS)
    attack_intent_hit = any(k in text_lower for k in ATTACK_INTENT_KEYWORDS)
    risky_source_hit = any(k in source.lower() for k in ["paste", "leak", "dump"])

    score = 0
    score += SCORING["credential_found"] if credential_found else 0
    score += SCORING["infra_keyword"] if infra_hit else 0
    score += SCORING["attack_intent"] if attack_intent_hit else 0
    score += SCORING["risky_source"] if risky_source_hit else 0
    score = min(score, 100)

    severity = classify_severity(score)
    hits = sum([credential_found, infra_hit, attack_intent_hit, risky_source_hit])
    confidence = confidence_from_score(score, hits)
    urgency = classify_urgency(severity)
    sector = detect_sector(text_lower)

    return {
        "source": clean_source_name(source),
        "title": title,
        "content": content,
        "credential_found": credential_found,
        "infra_hit": infra_hit,
        "attack_intent_hit": attack_intent_hit,
        "risky_source_hit": risky_source_hit,
        "score": score,
        "severity": severity,
        "confidence": confidence,
        "urgency": urgency,
        "sector": sector,
    }