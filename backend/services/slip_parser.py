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


def extract_slip_number(text: str) -> Optional[str]:
    if not text:
        return None

    candidates = re.findall(r"(?<!\d)(\d{6,8})(?!\d)", text)
    if not candidates:
        return None

    # GTM slips currently use six-digit numbers under the barcode.
    six_digit = [candidate for candidate in candidates if len(candidate) == 6]
    if six_digit:
        return six_digit[0]

    return candidates[0]


def parse_gul_ahmed_text(text: str) -> ParsedSlip:
    compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    slip = ParsedSlip()
    slip.slip_no = extract_slip_number(compact)

    patterns = {
        "vehicle_no": r"Vehicle\s*[:#-]?\s*([A-Z]{2,4}[-\s]?\d{2,5})",
        "party": r"Party\s*[:#-]?\s*([^\n]+)",
        "product": r"Product\s*[:#-]?\s*([^\n]+)",
        "location": r"Location\s*[:#-]?\s*([^\n]+)",
        "operator": r"(?:WB\s*Operator|Operator)\s*[:#-]?\s*([^\n]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, compact, re.IGNORECASE)
        if match:
            setattr(slip, field, match.group(1).strip())

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
