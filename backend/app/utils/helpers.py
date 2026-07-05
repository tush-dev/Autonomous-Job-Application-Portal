import uuid
import hashlib
from typing import Optional
from datetime import datetime, timezone


def generate_uuid() -> str:
    return str(uuid.uuid4())


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def truncate_text(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def parse_salary_range(salary_str: Optional[str]) -> tuple[Optional[int], Optional[int], str]:
    if not salary_str:
        return None, None, "USD"

    salary_str = salary_str.replace(",", "").replace("$", "").strip()
    parts = salary_str.split("-")

    try:
        if len(parts) == 2:
            return int(parts[0]), int(parts[1]), "USD"
        elif len(parts) == 1:
            value = int(parts[0])
            if "k" in salary_str.lower():
                value *= 1000
            return value, value, "USD"
    except (ValueError, TypeError):
        pass

    return None, None, "USD"
