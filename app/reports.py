from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates

from datetime import datetime
from datetime import timedelta

from app.dependencies import get_db, get_active_shift

from app.models import (
    Order,
    Reservation,
    ClubTable
)

from app.security import get_current_user

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

@router.get("/reports")
def reports_page(
        request: Request,
        db: Session = Depends(get_db),
):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    today = datetime.utcnow()

    month_start = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    day_start = today.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    orders_day = db.query(Order).filter(Order.created_at >= day_start).all()
    orders_month = db.query(Order).filter(Order.created_at >= month_start).all()

    day_revenue = sum(
        order.total_price for order in orders_day if order.status == "CLOSED"
    )

    month_revenue = sum(
        order.total_price for order in orders_month if order.status == "CLOSED"
    )

    reservations_count = db.query(Reservation).count()

    free_tables = db.query(ClubTable).filter(ClubTable.status == "FREE").count()
    occupied_tables = db.query(ClubTable).filter(ClubTable.status == "OCCUPIED").count()
    reserved_tables = db.query(ClubTable).filter(ClubTable.status == "RESERVED").count()

    # ИСПРАВЛЕННЫЙ БЛОК:
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "user": user,
            "day_revenue": day_revenue,
            "month_revenue": month_revenue,
            "reservations_count": reservations_count,
            "free_tables": free_tables,
            "occupied_tables": occupied_tables,
            "reserved_tables": reserved_tables,
            "orders_day": len(orders_day),
            "orders_month": len(orders_month)
        }
    )
