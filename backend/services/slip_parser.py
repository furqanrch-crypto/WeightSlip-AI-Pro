import re
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class ParsedSlip:
    slip_no: Optional[str] = None
    vehicle_no: Optional[str] = None
    party: Optional[str] = None
    product: Optional[str] = None
    first_weight: Optional[float] = None
    second_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_datetime: Optional[str] = None
    second_datetime: Optional[str] = None
    location: Optional[str] = None
    operator: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def _clean_weight(value: str) -> Optional[float]:
    if not value:
        return None
    cleaned = value.replace(",", "").replace("Kg", "").replace("KG", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _first_match(text: str, patterns: list[str]) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Some patterns intentionally match the full product name and do not
            # contain a capture group. Return group 1 only when it exists.
            return (match.group(1) if match.lastindex else match.group(0)).strip()
    return None


def extract_slip_number(text: str) -> Optional[str]:
    if not text:
        return None

    candidates = re.findall(r"(?<!\d)(\d{6,8})(?!\d)", text)
    if not candidates:
        return None

    six_digit = [candidate for candidate in candidates if len(candidate) == 6]
    return six_digit[0] if six_digit else candidates[0]


def _extract_vehicle(text: str) -> Optional[str]:
    match = re.search(r"\b([A-Z]{2,4})[-\s]?(\d{2,5})\b", text, re.IGNORECASE)
    if not match:
        return None
    return f"{match.group(1).upper()}-{match.group(2)}"


def _extract_location(text: str) -> Optional[str]:
    match = re.search(r"\bGTM\s*[- ]?\s*(\d{1,2})\b", text, re.IGNORECASE)
    if match:
        return f"GTM-{match.group(1)}"
    return None


def _extract_operator(text: str) -> Optional[str]:
    candidates = re.findall(r"\b([A-Z]\.?\s*[A-Za-z]{4,})\b", text)
    blocked = {
        "Vehicle", "Product", "Party", "Legend", "Weight", "Location",
        "Operator", "Status", "Driver", "Remarks", "Without", "Loaded",
        "Empty", "DAMPER", "Date", "Time", "View", "Incharge",
    }
    for candidate in candidates:
        cleaned = candidate.replace(" ", "")
        if cleaned.split(".")[-1] not in blocked and candidate not in blocked:
            return cleaned
    return None


def _extract_party(lines: list[str]) -> Optional[str]:
    for i, line in enumerate(lines):
        if re.fullmatch(r"Party", line, re.IGNORECASE) and i + 1 < len(lines):
            value = lines[i + 1]
            if not re.search(r"^(Product|Vehicle Type|DAMPER|Location)$", value, re.IGNORECASE):
                return value

    for line in lines:
        if re.search(r"\b(IMPEX|ENTERPRISES|TRADERS|INDUSTRIES|MILLS|COMPANY|CO\.)\b", line, re.IGNORECASE):
            return line
    return None


def _extract_product(lines: list[str], text: str) -> Optional[str]:
    product_patterns = [
        r"\bMISC\s*\([^\n]*?\)",
        r"\bMISC\s+DRIED\s+DUNG\b",
        r"\bDRIED\s*[- ]?\s*DUNG\b",
        r"\bCOW\s*(?:DUNG|MANURE)\b",
        r"\bRICE\s*HUSK\b",
        r"\bMUSTARD(?:\s*STRAW|\s*HUSK)?\b",
        r"\bSESAME(?:\s*HUSK|\s*STRAW)?\b",
        r"\bCOTTON(?:\s*STICKS?)?\b",
        r"\bSUGARCANE(?:\s*TRASH)?\b",
    ]
    value = _first_match(text, product_patterns)
    if value:
        return value

    blocked = re.compile(
        r"^(DAMPER|Date Time|WB Ref#?|WB Operator|Vehicle Status|Location|GTM-\d+)$",
        re.IGNORECASE,
    )
    for i, line in enumerate(lines):
        if re.fullmatch(r"Product", line, re.IGNORECASE):
            for candidate in lines[i + 1:i + 5]:
                if not blocked.search(candidate) and not re.fullmatch(r"Party|Vehicle", candidate, re.IGNORECASE):
                    return candidate
    return None


def _extract_datetimes(text: str) -> tuple[Optional[str], Optional[str]]:
    pattern = r"\b\d{1,2}[-/]?[A-Za-z]{3}[-/]?\d{2,4}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?\b"
    values = re.findall(pattern, text, re.IGNORECASE)
    first = values[0] if values else None
    second = values[1] if len(values) > 1 else None
    return first, second


def parse_gul_ahmed_text(text: str) -> ParsedSlip:
    compact_lines = _lines(text)
    compact = "\n".join(compact_lines)

    slip = ParsedSlip()
    slip.slip_no = extract_slip_number(compact)
    slip.vehicle_no = _extract_vehicle(compact)
    slip.party = _extract_party(compact_lines)
    slip.product = _extract_product(compact_lines, compact)
    slip.location = _extract_location(compact)
    slip.operator = _extract_operator(compact)
    slip.first_datetime, slip.second_datetime = _extract_datetimes(compact)

    weight_patterns = {
        "first_weight": r"1st\s*Weight\s*[:#-]?\s*([\d,]+(?:\.\d+)?)\s*(?:Kg|KG)?",
        "second_weight": r"2nd\s*Weight\s*[:#-]?\s*([\d,]+(?:\.\d+)?)\s*(?:Kg|KG)?",
        "net_weight": r"Net\s*Weight\s*[:#-]?\s*([\d,]+(?:\.\d+)?)\s*(?:Kg|KG)?",
    }

    for field, pattern in weight_patterns.items():
        match = re.search(pattern, compact, re.IGNORECASE)
        if match:
            setattr(slip, field, _clean_weight(match.group(1)))

    return slip
