from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi import Request

from fastapi.responses import RedirectResponse

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.security import get_current_user
from app.models import (
    ClubTable,
    Reservation,
    Order,
    Tobacco,
    Shift
)
from app.dependencies import get_db

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

@router.get("/dashboard")
def dashboard(
        request: Request,
        db: Session = Depends(get_db)
):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    # Ищем активную смену — теперь это нужно ТОЛЬКО ЗДЕСЬ
    active_shift = db.query(Shift).filter(Shift.end_time == None).first()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "timedelta": timedelta,  # Передай функцию в шаблон
            "active_shift": active_shift,
            "tables_count": db.query(ClubTable).count(),
            "reservations_count": db.query(Reservation).count(),
            "orders_count": db.query(Order).count(),
            "tobaccos_count": db.query(Tobacco).count()
        }
    )
