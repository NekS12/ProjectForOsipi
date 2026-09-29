from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import Form

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates

from datetime import datetime

from app.dependencies import get_db

from app.models import (
    Reservation,
    ClubTable,
    Shift
)

from app.security import get_current_user

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

@router.get("/reservations")
def reservations_page(
        request: Request,
        db: Session = Depends(get_db),
):

    user = get_current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    active_shift = db.query(Shift).filter(Shift.end_time == None).first()
    if not active_shift:
        # Если открытой смены нет, выкидываем на главную
        return RedirectResponse("/dashboard", status_code=302)

    reservations = db.query(Reservation).all()
    tables = db.query(ClubTable).filter(ClubTable.status == "FREE").all()

    return templates.TemplateResponse(
        request=request,
        name="reservations.html",
        context={
            "reservations": reservations,
            "tables": tables,
            "user": user,
        }
    )

@router.post("/reservations/create")
def create_reservation(
        customer_name: str = Form(...),
        phone: str = Form(...),
        guests: int = Form(...),
        reservation_time: str = Form(...),
        table_id: int = Form(...),
        db: Session = Depends(get_db)
):

    table = db.query(
        ClubTable
    ).filter(
        ClubTable.id == table_id
    ).first()

    try:
        parsed_time = datetime.strptime(
            reservation_time,
            "%d.%m.%Y %H:%M"
        )
    except ValueError:
        try:
            parsed_time = datetime.fromisoformat(reservation_time)
        except ValueError:
            parsed_time = datetime.utcnow()

    reservation = Reservation(
        customer_name=customer_name,
        phone=phone,
        guests=guests,
        reservation_time=parsed_time,
        table_id=table_id,
        status="ACTIVE"
    )

    table.status = "RESERVED"

    db.add(reservation)
    db.commit()

    return RedirectResponse(
        "/reservations",
        status_code=302
    )

@router.get("/reservations/cancel/{reservation_id}")
def cancel_reservation(
        reservation_id: int,
        db: Session = Depends(get_db)
):

    reservation = db.query(
        Reservation
    ).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation:

        table = db.query(
            ClubTable
        ).filter(
            ClubTable.id == reservation.table_id
        ).first()

        if table:
            table.status = "FREE"

        reservation.status = "CANCELLED"
        db.commit()

    return RedirectResponse(
        "/reservations",
        status_code=302
    )

@router.get("/reservations/checkin/{reservation_id}")
def checkin_reservation(
        reservation_id: int,
        db: Session = Depends(get_db)
):

    reservation = db.query(
        Reservation
    ).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation:

        reservation.status = "CHECKED_IN"

        table = db.query(
            ClubTable
        ).filter(
            ClubTable.id == reservation.table_id
        ).first()

        if table:
            table.status = "OCCUPIED"

        db.commit()

    return RedirectResponse(
        "/reservations",
        status_code=302
    )

@router.get("/reservations/edit/{id}")
def edit_page(
        id: int,
        request: Request,
        db: Session = Depends(get_db),
):

    user = get_current_user(request)

    reservation = db.query(
        Reservation
    ).filter(
        Reservation.id == id
    ).first()

    return templates.TemplateResponse(
        request=request,
        name="reservation_edit.html",
        context={
            "reservation": reservation,
            "user": user,
        }
    )

@router.post("/reservations/edit/{id}")
def save_edit(
        id: int,
        customer_name: str = Form(...),
        phone: str = Form(...),
        guests: int = Form(...),
        db: Session = Depends(get_db)
):

    reservation = db.query(
        Reservation
    ).filter(
        Reservation.id == id
    ).first()

    reservation.customer_name = customer_name
    reservation.phone = phone
    reservation.guests = guests

    db.commit()

    return RedirectResponse(
        "/reservations",
        status_code=302
    )
