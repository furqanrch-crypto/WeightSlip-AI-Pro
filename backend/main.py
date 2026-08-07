from datetime import datetime
from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, WeightSlip


app = FastAPI(
    title="WeightSlip AI Pro API",
    version="0.1.0",
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


def get_daily_upload_directory() -> Path:
    now = datetime.now()

    upload_dir = (
        ORIGINALS_DIR
        / str(now.year)
        / f"{now.month:02d}"
        / f"{now.day:02d}"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return upload_dir


@app.get("/")
def root():
    return {
        "app": "WeightSlip AI Pro",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/api/upload")
async def upload_weight_slip(
    file: UploadFile = File(...),
):
    if not file.filename:
        return {
            "success": False,
            "message": "Filename is missing.",
        }

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
    }

    if file.content_type not in allowed_types:
        return {
            "success": False,
            "message": "Unsupported image format.",
            "content_type": file.content_type,
        }

    extension = Path(file.filename).suffix.lower()

    if not extension:
        extension = ".jpg"

    internal_uuid = str(uuid.uuid4())
    stored_filename = f"{internal_uuid}{extension}"

    upload_directory = get_daily_upload_directory()
    save_path = upload_directory / stored_filename

    db = None
    record = None

    try:
        # Save image to disk
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        file_size = save_path.stat().st_size

        # Save upload record to database
        db = SessionLocal()

        record = WeightSlip(
            internal_uuid=internal_uuid,
            original_filename=file.filename,
            stored_path=str(save_path),
            processing_status="pending",
            validation_status="pending",
            duplicate=False,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "success": True,
            "database_id": record.id,
            "id": internal_uuid,
            "original_name": file.filename,
            "stored_filename": stored_filename,
            "stored_path": str(save_path),
            "size": file_size,
            "content_type": file.content_type,
            "processing_status": record.processing_status,
            "validation_status": record.validation_status,
            "duplicate": record.duplicate,
            "message": "Weight slip uploaded and saved successfully.",
        }

    except Exception as error:
        # Remove file if DB save or another step fails
        if save_path.exists():
            try:
                save_path.unlink()
            except Exception:
                pass

        if db is not None:
            db.rollback()

        return {
            "success": False,
            "message": "Unable to save uploaded weight slip.",
            "error": str(error),
        }

    finally:
        if db is not None:
            db.close()

        await file.close()