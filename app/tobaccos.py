from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import Form

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates

from app.dependencies import get_db
from app.models import Tobacco, Shift

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

@router.get("/tobaccos")
def tobaccos_page(
        request: Request,
        db: Session = Depends(get_db),
):
    active_shift = db.query(Shift).filter(Shift.end_time == None).first()
    if not active_shift:
        # Если открытой смены нет, выкидываем на главную
        return RedirectResponse("/dashboard", status_code=302)

    tobaccos = db.query(Tobacco).all()

    # ИСПРАВЛЕННЫЙ БЛОК:
    return templates.TemplateResponse(
        request=request,
        name="tobaccos.html",
        context={
            "tobaccos": tobaccos,
        }
    )


@router.post("/tobaccos/create")
def create_tobacco(
        brand: str = Form(...),
        name: str = Form(...),
        strength: str = Form(...),
        quantity: int = Form(...),
        db: Session = Depends(get_db)
):

    tobacco = Tobacco(
        brand=brand,
        name=name,
        strength=strength,
        quantity=quantity
    )

    db.add(tobacco)
    db.commit()

    return RedirectResponse(
        "/tobaccos",
        status_code=302
    )


@router.get("/tobaccos/delete/{id}")
def delete_tobacco(
        id: int,
        db: Session = Depends(get_db)
):

    tobacco = db.query(
        Tobacco
    ).filter(
        Tobacco.id == id
    ).first()

    if tobacco:

        db.delete(tobacco)
        db.commit()

    return RedirectResponse(
        "/tobaccos",
        status_code=302
    )
