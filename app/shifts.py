from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone  # Добавили timezone для точности

from app.dependencies import get_db, get_active_shift
from app.models import Shift, Order
from app.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Используем UTC для точности во всей системе
def get_now():
    return datetime.now(timezone.utc)


@router.post("/cashbox/open")
def open_shift(db: Session = Depends(get_db)):
    # Проверяем, нет ли уже открытой смены
    existing_shift = db.query(Shift).filter(Shift.end_time == None).first()

    if not existing_shift:
        new_shift = Shift(
            employee_name="Администратор",
            start_time=datetime.now() # Точное время сейчас
        )
        db.add(new_shift)
        db.commit()

    # Если вызываем через JS (fetch), редирект игнорируется,
    # если напрямую — вернет на страницу заказов
    return RedirectResponse("/dashboard", status_code=302)


@router.post("/cashbox/close")
def close_shift(
        actual_cash: float = Form(...),
        actual_card: float = Form(...),
        notes: str = Form(None),
        db: Session = Depends(get_db)
):
    current_shift = db.query(Shift).filter(Shift.end_time == None).first()

    if not current_shift:
        return RedirectResponse("/reports", status_code=302)

    closed_orders = db.query(Order).filter(
        Order.status == "CLOSED",
        Order.created_at >= current_shift.start_time
    ).all()

    total_calculated = sum(order.total_price for order in closed_orders)
    total_hookahs = sum(order.hookahs_count for order in closed_orders)

    total_actual = actual_cash + actual_card

    # Заполняем данные
    current_shift.end_time = datetime.now()  # Точное время завершения
    current_shift.system_revenue = total_calculated
    current_shift.actual_cash = actual_cash
    current_shift.actual_card = actual_card
    current_shift.total_actual = total_actual
    current_shift.discrepancy = total_actual - total_calculated
    current_shift.notes = notes
    current_shift.total_hookahs = total_hookahs
    current_shift.total_tobacco_used = total_hookahs * 25

    for order in closed_orders:
        order.status = "ARCHIVED"

    db.commit()
    return RedirectResponse("/reports", status_code=302)


@router.get("/cashbox/close-page")
def close_shift_page(
        request: Request,
        db: Session = Depends(get_db),
        active_shift=Depends(get_active_shift)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    current_shift = db.query(Shift).filter(Shift.end_time == None).order_by(Shift.id.desc()).first()

    if not current_shift:
        return RedirectResponse("/reports", status_code=302)

    # 1. Считаем заказы
    closed_orders = db.query(Order).filter(
        Order.status == "CLOSED",
        Order.created_at >= current_shift.start_time
    ).all()

    # 2. Общая сумма за смену
    total_calculated = sum(order.total_price for order in closed_orders)

    # 3. Количество кальянов за смену
    total_hookahs = sum(order.hookahs_count for order in closed_orders)

    # Сколько столов еще открыто
    open_orders_count = db.query(Order).filter(Order.status == "OPEN").count()

    return templates.TemplateResponse(
        request=request,
        name="close_session.html",
        context={
            "current_shift": current_shift,
            "total_calculated": total_calculated,  # Общая сумма
            "total_hookahs": total_hookahs,  # Количество кальянов
            "closed_orders_count": len(closed_orders),
            "open_orders_count": open_orders_count,
            "user": user,
            "active_shift": active_shift
        }
    )
