from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.dependencies import get_db
from app.models import ClubTable, Shift
from app.security import get_current_user

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


@router.get("/tables")
def tables_page(
        request: Request,
        error: str = None,  # Подхватываем ошибку из параметров URL, если она передана
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
        # Если открытой смены нет, отправляем на главную панели
        return RedirectResponse("/dashboard", status_code=302)

    tables = db.query(
        ClubTable
    ).order_by(
        ClubTable.number
    ).all()

    # Передаем значение error в контекст HTML-шаблона
    return templates.TemplateResponse(
        request=request,
        name="tables.html",
        context={
            "tables": tables,
            "user": user,
            "error": error,
        }
    )


@router.post("/tables/create")
def create_table(
        number: int = Form(...),
        capacity: int = Form(...),
        db: Session = Depends(get_db)
):
    # Проверяем, существует ли уже столик с таким номером в базе данных
    existing_table = db.query(ClubTable).filter(ClubTable.number == number).first()

    if existing_table:
        # Если нашли дубликат, перенаправляем обратно на /tables и добавляем текст ошибки
        return RedirectResponse(
            f"/tables?error=Столик с номером {number} уже существует!",
            status_code=302
        )

    # Если проверка пройдена, спокойно создаем новую запись
    table = ClubTable(
        number=number,
        capacity=capacity,
        status="FREE"
    )

    db.add(table)
    db.commit()

    return RedirectResponse(
        "/tables",
        status_code=302
    )


@router.get("/tables/status/{table_id}/{status}")
def change_status(
        table_id: int,
        status: str,
        db: Session = Depends(get_db)
):
    table = db.query(
        ClubTable
    ).filter(
        ClubTable.id == table_id
    ).first()

    if table:
        table.status = status
        db.commit()

    return RedirectResponse(
        "/tables",
        status_code=302
    )


@router.get("/tables/delete/{table_id}")
def delete_table(
        table_id: int,
        db: Session = Depends(get_db)
):
    table = db.query(
        ClubTable
    ).filter(
        ClubTable.id == table_id
    ).first()

    if table:
        db.delete(table)
        db.commit()

    return RedirectResponse(
        "/tables",
        status_code=302
    )
