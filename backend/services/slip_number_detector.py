import re


SLIP_PATTERN = re.compile(r"\b\d{5,8}\b")


def extract_slip_number(ocr_result):
    text = ""

    for block in ocr_result[0]:
        text += " " + block[1][0]

    matches = SLIP_PATTERN.findall(text)

    if not matches:
        return None

    return matches[0]