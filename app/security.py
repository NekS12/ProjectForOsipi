from fastapi import Request
from fastapi.responses import RedirectResponse

from app.database import SessionLocal
from app.models import User


def get_current_user(request: Request):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    db = SessionLocal()

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    db.close()

    return user


def login_required(request: Request):

    user = get_current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=302
        )

    return user
