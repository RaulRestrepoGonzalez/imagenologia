from fastapi import APIRouter
from ..services.notification_service import send_email

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

@router.post("/send")
async def send_notification(email: str, subject: str, message: str):
    result = await send_email(email, subject, message)
    return {"status": result}
