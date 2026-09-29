from urllib.parse import quote

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from datetime import datetime

# Импортируем необходимые модели (Добавили Tobacco и Shift)
from app.dependencies import get_db
from app.models import Reservation, Order, ClubTable, Hookah, Tobacco, Shift
from app.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/orders")
def orders_page(
        request: Request,
        db: Session = Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # --- ПРОВЕРКА ОТКРЫТОЙ СМЕНЫ ---
    # Ищем смену, у которой нет времени закрытия (end_time)
    active_shift = db.query(Shift).filter(Shift.end_time == None).first()

    # Если открытой смены нет, перекидываем пользователя на главную страницу
    if not active_shift:
        error_msg = quote("Внимание! Для доступа к заказам необходимо открыть смену.")
        return RedirectResponse(f"/?error={error_msg}", status_code=302)

    orders = db.query(Order).order_by(Order.id.desc()).all()
    tables = db.query(ClubTable).all()
    hookahs = db.query(Hookah).all()

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "orders": orders,
            "tables": tables,
            "hookahs": hookahs,
            "user": user,
            "active_shift": active_shift  # Передаем активную смену в шаблон (полезно для шапки сайта)
        }
    )


@router.post("/orders/create")
def create_order(
        table_id: int = Form(...),
        hookah_id: int = Form(...),
        hookahs_count: int = Form(...),
        db: Session = Depends(get_db)
):
    # ПРОВЕРКА 1: Запрещаем создавать заказ, если на столе уже есть ОТКРЫТЫЙ заказ
    existing_order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.status == "OPEN"
    ).first()

    if existing_order:
        return RedirectResponse("/orders", status_code=302)

    # 1. Находим выбранный кальян и его цену
    hookah = db.query(Hookah).filter(Hookah.id == hookah_id).first()
    calculated_price = hookah.price * hookahs_count

    # 2. Ищем активную бронь (если она есть)
    reservation = db.query(Reservation).filter(
        Reservation.table_id == table_id,
        Reservation.status == "CHECKED_IN"
    ).first()

    # 3. Создаем заказ с жесткой привязкой к table_id
    order = Order(
        table_id=table_id,
        reservation_id=reservation.id if reservation else None,
        hookah_id=hookah_id,
        hookahs_count=hookahs_count,
        total_price=calculated_price,
        status="OPEN",
        created_at=datetime.now()
    )

    # 4. Меняем статус стола на "ЗАНЯТ"
    table = db.query(ClubTable).filter(ClubTable.id == table_id).first()
    if table:
        table.status = "OCCUPIED"

    db.add(order)
    db.commit()

    return RedirectResponse("/orders", status_code=302)


@router.get("/orders/close/{order_id}")
def close_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if order:
        order.status = "CLOSED"

        # --- 1. АВТОМАТИЧЕСКОЕ СПИСАНИЕ ТАБАКА ---
        # Находим кальян, который был в заказе
        hookah = db.query(Hookah).filter(Hookah.id == order.hookah_id).first()
        if hookah:
            # Ищем табак, у которого название строго совпадает с названием кальяна
            tobacco = db.query(Tobacco).filter(Tobacco.name == hookah.name).first()
            if tobacco:
                # Списываем по 25 грамм за каждый кальян в этом заказе
                tobacco.quantity -= (25 * order.hookahs_count)

        # --- 2. ОСВОБОЖДАЕМ СТОЛ ---
        if order.table_id:
            table = db.query(ClubTable).filter(ClubTable.id == order.table_id).first()
            if table:
                table.status = "FREE"

        # --- 3. ЗАКРЫВАЕМ БРОНЬ ---
        if order.reservation_id:
            reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
            if reservation:
                reservation.status = "COMPLETED"

        db.commit()

    return RedirectResponse("/orders", status_code=302)


@router.get("/orders/delete/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        # Если мы удаляем открытый заказ (например, создали по ошибке), нужно освободить стол
        if order.status == "OPEN" and order.table_id:
            table = db.query(ClubTable).filter(ClubTable.id == order.table_id).first()
            if table:
                table.status = "FREE"

        db.delete(order)
        db.commit()
    return RedirectResponse("/orders", status_code=302)
