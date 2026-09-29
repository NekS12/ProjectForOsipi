from app.database import SessionLocal
from app.models import User, ClubTable, Hookah, Tobacco # Добавили импорт Tobacco
from app.auth import hash_password

db = SessionLocal()

# 1. Создаем админа
if not db.query(User).filter(User.username == "admin").first():
    admin = User(
        username="admin",
        password=hash_password("admin"),
        role="OWNER"
    )
    db.add(admin)

# 2. Создаем столики
for i in range(1, 11):
    exists = db.query(ClubTable).filter(ClubTable.number == i).first()
    if not exists:
        db.add(ClubTable(number=i, capacity=4, status="FREE"))

# 3. Добавляем кальяны
hookahs_data = [
    {"name": "Стандарт", "price": 1600.0},
    {"name": "Dogma", "price": 1900.0},
    {"name": "Bonche", "price": 1900.0},
    {"name": "Special", "price": 2000.0},
    {"name": "Parfume", "price": 3000.0},
    {"name": "Tangiers", "price": 2000.0}
]

for h in hookahs_data:
    # Проверяем, есть ли уже такой кальян, чтобы не дублировать
    if not db.query(Hookah).filter(Hookah.name == h["name"]).first():
        db.add(Hookah(name=h["name"], price=h["price"], status="FREE"))

# 4. Добавляем табак на склад (Названия 'name' строго совпадают с кальянами!)
tobacco_data = [
    {"brand": "MustHave/DarkSide", "name": "Стандарт", "strength": "Средняя", "quantity": 1000, "description": "Базовые табаки для стандартных забивок"},
    {"brand": "Dogma", "name": "Dogma", "strength": "Крепкая", "quantity": 500, "description": "Сигарный бленд"},
    {"brand": "Bonche", "name": "Bonche", "strength": "Крепкая", "quantity": 500, "description": "Сигарный лист премиум"},
    {"brand": "Mix", "name": "Special", "strength": "Разная", "quantity": 500, "description": "Авторские миксы заведения"},
    {"brand": "Satyr", "name": "Parfume", "strength": "Средняя", "quantity": 250, "description": "Парфюмерная линейка"},
    {"brand": "Tangiers", "name": "Tangiers", "strength": "Очень крепкая", "quantity": 500, "description": "Американский крафт"}
]

for t in tobacco_data:
    # Проверяем по имени, чтобы не создать дубликаты при повторном запуске скрипта
    if not db.query(Tobacco).filter(Tobacco.name == t["name"]).first():
        db.add(Tobacco(
            brand=t["brand"],
            name=t["name"],
            strength=t["strength"],
            quantity=t["quantity"],
            description=t["description"]
        ))

db.commit()
print("Database initialized: Admin, Tables, Hookahs, and Tobacco stock created.")
