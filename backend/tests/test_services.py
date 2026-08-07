from services.slip_parser import extract_slip_number, parse_gul_ahmed_text
from services.validation import validate_weights


def test_extracts_gtm_slip_number():
    text = "GUL AHMED TEXTILE MILLS LTD\nBARCODE\n319553\nVehicle TAE-522"
    assert extract_slip_number(text) == "319553"


def test_parses_core_gtm_fields():
    text = """
    GUL AHMED TEXTILE MILLS LTD
    319553
    Vehicle TAE-522
    Party RAFIQUE IMPEX
    Product MISC (DRIED - DUNG)
    Location GTM-3
    1st Weight 23,680 Kg
    2nd Weight 16,760 Kg
    Net Weight 6,920 Kg
    """

    parsed = parse_gul_ahmed_text(text)

    assert parsed.slip_no == "319553"
    assert parsed.vehicle_no == "TAE-522"
    assert parsed.first_weight == 23680
    assert parsed.second_weight == 16760
    assert parsed.net_weight == 6920


def test_weight_validation_passes():
    result = validate_weights(23680, 16760, 6920)
    assert result["valid"] is True
    assert result["status"] == "valid"


def test_weight_validation_flags_mismatch():
    result = validate_weights(23680, 16760, 7000)
    assert result["valid"] is False
    assert result["status"] == "review_required"
