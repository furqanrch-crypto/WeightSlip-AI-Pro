from database import SessionLocal, WeightSlip
from services.duplicate_detector import find_duplicate_by_slip_no
from services.image_preprocessor import fallback_preprocess_images, preprocess_image
from services.ocr_engine import run_ocr
from services.slip_number_detector import extract_slip_number
from services.slip_parser import parse_gul_ahmed_text
from services.validation import validate_weights


def _quality_score(parsed, validation: dict) -> int:
    """Score only the fields required in the operational report."""
    score = 0

    if parsed.slip_no:
        score += 8
    if parsed.vehicle_no:
        score += 3
    if parsed.product:
        score += 3
    if parsed.first_datetime or parsed.second_datetime:
        score += 2

    if parsed.first_weight is not None:
        score += 5
    if parsed.second_weight is not None:
        score += 5
    if parsed.net_weight is not None:
        score += 5

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


def process_weight_slip(record_id: int) -> None:
    """Run OCR, one fallback pass, parsing, validation and duplicate detection."""
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

        needs_retry = (
            not best_validation.get("valid")
            or not best_parsed.slip_no
            or best_parsed.first_weight is None
            or best_parsed.second_weight is None
            or best_parsed.net_weight is None
        )

        if needs_retry:
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
            record.processing_status = (
                "completed" if best_validation["valid"] else "review_required"
            )
            if not best_validation["valid"]:
                record.error_message = best_validation.get("message")
            else:
                record.error_message = None

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
