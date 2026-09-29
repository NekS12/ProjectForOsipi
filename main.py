from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app import dashboard
from app import auths
from app import tables
from app import reservations
from app import tobaccos

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Hookah Club"
)

app.include_router(
    tobaccos.router
)

app.include_router(
    auths.router
)

app.include_router(
    reservations.router
)

app.include_router(
    dashboard.router
)

app.include_router(
    tables.router
)

from app import orders

app.include_router(
    orders.router
)

from app import reports

app.include_router(
    reports.router
)

from app import shifts
app.include_router(
    shifts.router
)
