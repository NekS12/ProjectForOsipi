from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import Form

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.models import User

from app.auth import verify_password

router = APIRouter()

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@router.get("/")
def root_redirect():
    return RedirectResponse(
        url="/dashboard",
        status_code=302
    )

@router.post("/login")
def login_post(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    user = db.query(
        User
    ).filter(
        User.username == username
    ).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Пользователь не найден"}
        )

    if not verify_password(password, user.password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный пароль"}
        )

    response = RedirectResponse(
        "/dashboard",
        status_code=302
    )

    response.set_cookie(
        key="user_id",
        value=str(user.id)
    )

    return response


@router.get("/logout")
def logout():

    response = RedirectResponse(
        "/login",
        status_code=302
    )

    response.delete_cookie(
        "user_id"
    )

    return response
