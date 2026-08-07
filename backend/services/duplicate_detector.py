from typing import Optional

from sqlalchemy.orm import Session

from database import WeightSlip


def find_duplicate_by_slip_no(
    db: Session,
    slip_no: Optional[str],
    exclude_record_id: Optional[int] = None,
) -> Optional[WeightSlip]:
    if not slip_no:
        return None

    query = db.query(WeightSlip).filter(WeightSlip.slip_no == slip_no)

    if exclude_record_id is not None:
        query = query.filter(WeightSlip.id != exclude_record_id)

    return query.order_by(WeightSlip.id.asc()).first()
