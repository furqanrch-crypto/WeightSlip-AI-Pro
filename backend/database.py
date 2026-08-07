from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "storage" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'weightslip.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class WeightSlip(Base):
    __tablename__ = "weight_slips"

    id = Column(Integer, primary_key=True, index=True)

    internal_uuid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    slip_no = Column(
        String,
        nullable=True,
        index=True,
    )

    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)

    vehicle_no = Column(String, nullable=True)
    party = Column(String, nullable=True)
    product = Column(String, nullable=True)

    first_weight = Column(Float, nullable=True)
    second_weight = Column(Float, nullable=True)
    net_weight = Column(Float, nullable=True)

    first_datetime = Column(String, nullable=True)
    second_datetime = Column(String, nullable=True)

    location = Column(String, nullable=True)
    operator = Column(String, nullable=True)

    processing_status = Column(
        String,
        default="pending",
        nullable=False,
    )

    validation_status = Column(
        String,
        default="pending",
        nullable=False,
    )

    duplicate = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    duplicate_of = Column(
        Integer,
        nullable=True,
    )

    confidence = Column(
        Float,
        nullable=True,
    )

    error_message = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


Base.metadata.create_all(bind=engine)