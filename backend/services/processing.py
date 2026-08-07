from database import SessionLocal, WeightSlip
from services.duplicate_detector import find_duplicate_by_slip_no
from services.image_preprocessor import fallback_preprocess_images, preprocess_image
from services.ocr_engine import run_ocr
from services.slip_number_detector import extract_slip_number
from services.slip_parser import parse_gul_ahmed_text
from services.validation import validate_weights


def _quality_score(parsed, validation: dict) -> int:
    """Score only the eight fields required in the final report."""
    score = 0

    if parsed.slip_no:
        score += 8
    if parsed.party:
        score += 4
    if parsed.vehicle_no:
        score += 4
    if parsed.product:
        score += 4
    if parsed.first_datetime or parsed.second_datetime:
        score += 3

    if parsed.first_weight is not None:
        score += 5
    if parsed.second_weight is not None:
        score += 5
    if parsed.net_weight is not None:
        score += 5

    # Correct weight arithmetic is the strongest quality signal.
    if validation.get("valid"):
        score += 20

    return score


def _parse_ocr_result(ocr_result: dict):
    ocr_text = ocr_result.get("text", "")
    parsed = parse_gul_ahmed_text(ocr_text)

    detected_slip_no = extract_slip_number(ocr_result)
    if detected_slip_no:
        parsed.slip_no = detected_slip_no

    validation = validate_weights(
        parsed.first_weight,
        parsed.second_weight,
        parsed.net_weight,
    )

    return parsed, validation


def _missing_required_field(parsed, validation: dict) -> bool:
    """Return True when any field required in the final Excel/report is missing."""
    return (
        not parsed.slip_no
        or not parsed.party
        or not parsed.vehicle_no
        or not parsed.product
        or not (parsed.first_datetime or parsed.second_datetime)
        or parsed.first_weight is None
        or parsed.second_weight is None
        or parsed.net_weight is None
        or not validation.get("valid")
    )


def process_weight_slip(record_id: int) -> None:
    """Run OCR, at most one fallback pass, parsing, validation and duplicate detection."""
    db = SessionLocal()

    try:
        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is None:
            return

        record.processing_status = "preprocessing"
        record.error_message = None
        db.commit()

        primary_image = preprocess_image(record.stored_path)

        record.processing_status = "ocr"
        db.commit()

        primary_result = run_ocr(primary_image)
        best_result = primary_result
        best_parsed, best_validation = _parse_ocr_result(primary_result)
        best_score = _quality_score(best_parsed, best_validation)

        # One retry maximum. We retry only when one of the eight report fields
        # is missing/invalid, so unnecessary OCR work does not block the queue.
        if _missing_required_field(best_parsed, best_validation):
            record.processing_status = "ocr_retry"
            db.commit()

            variants = fallback_preprocess_images(record.stored_path)
            if variants:
                candidate_result = run_ocr(variants[0])
                candidate_parsed, candidate_validation = _parse_ocr_result(candidate_result)
                candidate_score = _quality_score(candidate_parsed, candidate_validation)

                if candidate_score > best_score:
                    best_result = candidate_result
                    best_parsed = candidate_parsed
                    best_validation = candidate_validation
                    best_score = candidate_score

        record.processing_status = "parsing"
        db.commit()

        parsed_data = best_parsed.to_dict()
        for field, value in parsed_data.items():
            if value is not None and hasattr(record, field):
                setattr(record, field, value)

        record.confidence = best_result.get("confidence")
        record.validation_status = best_validation["status"]

        duplicate_record = find_duplicate_by_slip_no(
            db,
            record.slip_no,
            exclude_record_id=record.id,
        )

        if duplicate_record is not None:
            record.duplicate = True
            record.duplicate_of = duplicate_record.id
            record.processing_status = "duplicate"
        elif not record.slip_no:
            record.duplicate = False
            record.duplicate_of = None
            record.processing_status = "review_required"
            record.error_message = "Unable to detect weight slip number."
        else:
            record.duplicate = False
            record.duplicate_of = None

            missing_fields = []
            if not record.party:
                missing_fields.append("party")
            if not record.vehicle_no:
                missing_fields.append("vehicle number")
            if not record.product:
                missing_fields.append("product")
            if not (record.first_datetime or record.second_datetime):
                missing_fields.append("date")
            if record.first_weight is None:
                missing_fields.append("1st weight")
            if record.second_weight is None:
                missing_fields.append("2nd weight")
            if record.net_weight is None:
                missing_fields.append("net weight")

            if best_validation["valid"] and not missing_fields:
                record.processing_status = "completed"
                record.error_message = None
            else:
                record.processing_status = "review_required"
                if missing_fields:
                    record.error_message = "Missing required fields: " + ", ".join(missing_fields)
                else:
                    record.error_message = best_validation.get("message")

        db.commit()

    except Exception as error:
        db.rollback()

        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is not None:
            record.processing_status = "failed"
            record.error_message = str(error)
            db.commit()

    finally:
        db.close()
