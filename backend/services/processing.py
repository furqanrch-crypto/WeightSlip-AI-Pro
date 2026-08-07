from database import SessionLocal, WeightSlip
from services.duplicate_detector import find_duplicate_by_slip_no
from services.image_preprocessor import preprocess_image
from services.ocr_engine import run_ocr
from services.slip_number_detector import extract_slip_number
from services.slip_parser import parse_gul_ahmed_text
from services.validation import validate_weights


def process_weight_slip(record_id: int) -> None:
    """Run OCR, parsing, validation, and slip-number duplicate detection."""
    db = SessionLocal()

    try:
        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is None:
            return

        record.processing_status = "preprocessing"
        record.error_message = None
        db.commit()

        image = preprocess_image(record.stored_path)

        record.processing_status = "ocr"
        db.commit()

        ocr_result = run_ocr(image)
        ocr_text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence")

        record.processing_status = "parsing"
        db.commit()

        parsed = parse_gul_ahmed_text(ocr_text)
        parsed_data = parsed.to_dict()

        # Prefer the dedicated slip-number detector because duplicate logic
        # depends on this field being as reliable as possible.
        detected_slip_no = extract_slip_number(ocr_result)
        if detected_slip_no:
            parsed_data["slip_no"] = detected_slip_no

        for field, value in parsed_data.items():
            if value is not None and hasattr(record, field):
                setattr(record, field, value)

        record.confidence = confidence

        validation = validate_weights(
            record.first_weight,
            record.second_weight,
            record.net_weight,
        )
        record.validation_status = validation["status"]

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
                "completed" if validation["valid"] else "review_required"
            )

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
