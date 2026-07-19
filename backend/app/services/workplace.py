"""Normalize workplace type from inconsistent external job feeds."""


def classify_workplace(remote: object, location: object = None, description: object = None) -> str:
    declared = str(remote or "").strip().lower().replace("-", "")
    if declared in {"remote", "hybrid", "onsite"}:
        return declared

    location_text = str(location or "").lower()
    description_text = str(description or "").lower()
    text = f"{location_text} {description_text[:5000]}"

    if any(term in text for term in ("hybrid", "flexible workplace", "days in office", "days per week in office")):
        return "hybrid"
    if any(term in text for term in ("fully remote", "100% remote", "remote position", "work from home", "work from anywhere")):
        return "remote"
    if any(term in text for term in ("on-site", "onsite", "in-office", "in office", "office-based")):
        return "onsite"
    if "remote" in location_text:
        return "remote"

    # A concrete location with no remote language is normally an on-site role.
    if location_text.strip() and location_text.strip() not in {"unspecified", "n/a", "worldwide", "anywhere"}:
        return "onsite"
    return "unspecified"
