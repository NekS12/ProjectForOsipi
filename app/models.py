from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()



# ======================
# Пользователи
# ======================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ======================
# Столики
# ======================

class ClubTable(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True)

    number = Column(Integer, unique=True)

    capacity = Column(Integer)

    status = Column(
        String(30),
        default="FREE"
    )

    reservations = relationship(
        "Reservation",
        back_populates="table"
    )


# ======================
# Бронирование
# ======================

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)

    customer_name = Column(String(255))

    phone = Column(String(50))

    guests = Column(Integer)

    reservation_time = Column(DateTime)

    status = Column(
        String(30),
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    table_id = Column(
        Integer,
        ForeignKey("tables.id")
    )

    table = relationship(
        "ClubTable",
        back_populates="reservations"
    )

    orders = relationship(
        "Order",
        back_populates="reservation"
    )


# ======================
# Табак
# ======================

class Tobacco(Base):
    __tablename__ = "tobaccos"

    id = Column(Integer, primary_key=True)

    brand = Column(String(100))

    name = Column(String(100))

    strength = Column(String(50))

    quantity = Column(Integer)

    description = Column(Text)


# ======================
# Кальяны
# ======================

class Hookah(Base):
    __tablename__ = "hookahs"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)  # Добавили обязательное поле цены

    # Статус и заметки можно оставить, если они нужны
    status = Column(String(30), default="FREE")
    notes = Column(Text)



class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    reservation_id = Column(
        Integer,
        ForeignKey("reservations.id")
    )

    total_price = Column(
        Float,
        default=0
    )

    status = Column(
        String(50),
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    reservation = relationship(
        "Reservation",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    hookah_id = Column(Integer, ForeignKey("hookahs.id"), nullable=True)
    hookahs_count = Column(Integer, default=0)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    table = relationship("ClubTable")  # Чтобы работала связь

# ======================
# Позиции заказа
# ======================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    quantity = Column(Integer)

    price = Column(Float)

    order = relationship(
        "Order",
        back_populates="items"
    )



# ======================
# Смены
# ======================

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True)
    employee_name = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True) # Изначально смену открывают, закрывают в конце
    role = Column(String(50))

    # --- НОВЫЕ КОЛОНКИ ДЛЯ ЗАКРЫТИЯ КАССЫ ---
    system_revenue = Column(Float, default=0.0)  # Сколько насчитала система по чекам
    actual_cash = Column(Float, default=0.0)     # Сколько сдали наличкой
    actual_card = Column(Float, default=0.0)     # Сколько сдали по терминалу
    total_actual = Column(Float, default=0.0)    # Факт всего (actual_cash + actual_card)
    discrepancy = Column(Float, default=0.0)     # Разница (Факт минус Система)
    notes = Column(Text, nullable=True)          # Расходы, закупки, комментарии
    total_hookahs = Column(Integer, default=0)  # Всего кальянов за смену
    total_tobacco_used = Column(Float, default=0.0)
