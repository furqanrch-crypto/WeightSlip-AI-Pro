import re
from typing import Iterable


SLIP_PATTERN = re.compile(r"(?<!\d)(\d{5,8})(?!\d)")


def _candidate_numbers(lines: Iterable[str]) -> list[str]:
    candidates: list[str] = []

    for line in lines:
        cleaned = str(line).strip()
        candidates.extend(SLIP_PATTERN.findall(cleaned))

    return candidates


def extract_slip_number(ocr_result) -> str | None:
    """Extract the most likely weighbridge slip number from normalized OCR."""
    if isinstance(ocr_result, dict):
        lines = ocr_result.get("lines") or []
        text = ocr_result.get("text") or ""
    else:
        lines = []
        text = str(ocr_result or "")

    candidates = _candidate_numbers(lines)

    if not candidates:
        candidates = SLIP_PATTERN.findall(text)

    if not candidates:
        return None

    # Gul Ahmed slip IDs in the supplied format are normally 6 digits.
    six_digit = [candidate for candidate in candidates if len(candidate) == 6]
    if six_digit:
        return six_digit[0]

    return candidates[0]
