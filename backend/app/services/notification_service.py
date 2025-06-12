import smtplib
from email.message import EmailMessage
from ..config import settings

async def send_email(to: str, subject: str, content: str):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = subject
        msg["From"] = settings.mail_sender
        msg["To"] = to
        # Simulación (reemplazar por lógica real o SMTP)
        print(f"Enviado a {to}: {subject}")
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"
