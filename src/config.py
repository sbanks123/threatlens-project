INDIAN_INFRA_KEYWORDS = [
    "uidai", "aadhaar", "npci", "upi", "irctc", "rbi", "isro",
    "power grid", "ntpc", "railway", "railways", "bsnl", "airtel", "gov", "government"
]

SECTOR_KEYWORDS = {
    "Banking & Finance": ["rbi", "npci", "upi", "bank", "payment gateway"],
    "Government": ["uidai", "aadhaar", "gov", "government", "ministry"],
    "Transport": ["irctc", "railway", "railways", "airport", "aviation"],
    "Energy": ["ntpc", "power grid", "grid", "substation", "electricity"],
    "Defense & Space": ["isro", "army", "defence", "defense", "navy", "air force"],
    "Telecom": ["bsnl", "airtel", "jio", "vodafone", "telecom"],
}

ATTACK_INTENT_KEYWORDS = [
    "breach", "dump", "selling access", "ransomware", "ddos", "exploit",
    "database leak", "credential", "admin panel", "exfiltration", "attack plan",
    "take down", "deface", "malware", "phishing campaign"
]

RISKY_SOURCE_BONUS = 10

SCORING = {
    "credential_found": 40,
    "infra_keyword": 30,
    "attack_intent": 20,
    "risky_source": RISKY_SOURCE_BONUS,
}

SEVERITY_BANDS = [
    (0, 25, "LOW"),
    (26, 50, "MEDIUM"),
    (51, 75, "HIGH"),
    (76, 100, "CRITICAL"),
]
