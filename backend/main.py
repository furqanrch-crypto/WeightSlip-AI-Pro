from datetime import datetime
from pathlib import Path
import shutil
import uuid

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import SessionLocal, WeightSlip
from services.duplicate_detector import find_duplicate_by_slip_no
from services.processing import process_weight_slip
from services.slip_parser import parse_gul_ahmed_text
from services.validation import validate_weights


app = FastAPI(
    title="WeightSlip AI Pro API",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
ORIGINALS_DIR = STORAGE_DIR / "originals"


class OCRTextRequest(BaseModel):
    text: str


def get_daily_upload_directory() -> Path:
    now = datetime.now()
    upload_dir = (
        ORIGINALS_DIR
        / str(now.year)
        / f"{now.month:02d}"
        / f"{now.day:02d}"
    )
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def serialize_record(record: WeightSlip) -> dict:
    return {
        "id": record.id,
        "internal_uuid": record.internal_uuid,
        "slip_no": record.slip_no,
        "original_filename": record.original_filename,
        "stored_path": record.stored_path,
        "vehicle_no": record.vehicle_no,
        "party": record.party,
        "product": record.product,
        "first_weight": record.first_weight,
        "second_weight": record.second_weight,
        "net_weight": record.net_weight,
        "first_datetime": record.first_datetime,
        "second_datetime": record.second_datetime,
        "location": record.location,
        "operator": record.operator,
        "processing_status": record.processing_status,
        "validation_status": record.validation_status,
        "duplicate": record.duplicate,
        "duplicate_of": record.duplicate_of,
        "confidence": record.confidence,
        "error_message": record.error_message,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@app.get("/")
def root():
    return {
        "app": "WeightSlip AI Pro",
        "status": "running",
        "version": "0.3.0",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/records")
def list_records(limit: int = 100):
    safe_limit = max(1, min(limit, 1000))
    db = SessionLocal()

    try:
        records = (
            db.query(WeightSlip)
            .order_by(WeightSlip.id.desc())
            .limit(safe_limit)
            .all()
        )
        return {
            "success": True,
            "count": len(records),
            "records": [serialize_record(record) for record in records],
        }
    finally:
        db.close()


@app.get("/api/records/{record_id}")
def get_record(record_id: int):
    db = SessionLocal()

    try:
        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Weight slip record not found.")
        return {"success": True, "record": serialize_record(record)}
    finally:
        db.close()


@app.post("/api/upload")
async def upload_weight_slip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image format: {file.content_type}",
        )

    extension = Path(file.filename).suffix.lower() or ".jpg"
    internal_uuid = str(uuid.uuid4())
    stored_filename = f"{internal_uuid}{extension}"
    upload_directory = get_daily_upload_directory()
    save_path = upload_directory / stored_filename

    db = None

    try:
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = save_path.stat().st_size

        db = SessionLocal()
        record = WeightSlip(
            internal_uuid=internal_uuid,
            original_filename=file.filename,
            stored_path=str(save_path),
            processing_status="queued",
            validation_status="pending",
            duplicate=False,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        record_id = record.id
        background_tasks.add_task(process_weight_slip, record_id)

        return {
            "success": True,
            "database_id": record_id,
            "id": internal_uuid,
            "original_name": file.filename,
            "stored_filename": stored_filename,
            "stored_path": str(save_path),
            "size": file_size,
            "content_type": file.content_type,
            "processing_status": "queued",
            "validation_status": record.validation_status,
            "duplicate": record.duplicate,
            "message": "Weight slip uploaded. OCR processing has started automatically.",
        }

    except Exception as error:
        if save_path.exists():
            try:
                save_path.unlink()
            except OSError:
                pass

        if db is not None:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to save uploaded weight slip: {error}",
        ) from error

    finally:
        if db is not None:
            db.close()
        await file.close()


@app.post("/api/records/{record_id}/reprocess")
def reprocess_record(record_id: int, background_tasks: BackgroundTasks):
    db = SessionLocal()

    try:
        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Weight slip record not found.")

        record.processing_status = "queued"
        record.error_message = None
        db.commit()
        background_tasks.add_task(process_weight_slip, record_id)

        return {
            "success": True,
            "record_id": record_id,
            "processing_status": "queued",
        }
    finally:
        db.close()


@app.post("/api/records/{record_id}/apply-ocr-text")
def apply_ocr_text(record_id: int, payload: OCRTextRequest):
    db = SessionLocal()

    try:
        record = db.query(WeightSlip).filter(WeightSlip.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Weight slip record not found.")

        parsed = parse_gul_ahmed_text(payload.text)
        parsed_data = parsed.to_dict()

        for field, value in parsed_data.items():
            if value is not None and hasattr(record, field):
                setattr(record, field, value)

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
        else:
            record.duplicate = False
            record.duplicate_of = None
            record.processing_status = (
                "completed" if validation["valid"] else "review_required"
            )

        db.commit()
        db.refresh(record)

        return {
            "success": True,
            "record": serialize_record(record),
            "parsed": parsed_data,
            "validation": validation,
        }

    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unable to apply OCR text: {error}",
        ) from error
    finally:
        db.close()
