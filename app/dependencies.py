from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models import Shift

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Временно замени функцию на эту в app/dependencies.py
def get_active_shift(db: Session = Depends(get_db)):
    shift = db.query(Shift).order_by(Shift.id.desc()).first()
    # Если последняя смена есть и у неё нет end_time, возвращаем её
    if shift and shift.end_time is None:
        return shift
    return None
