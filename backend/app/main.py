from fastapi import FastAPI
from .config import settings
from .routers import auth, patients, orders, appointments, notifications

app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(orders.router)
app.include_router(appointments.router)
app.include_router(notifications.router)

@app.get("/")
async def root():
    return {"message": f"{settings.app_name} API activa"}

