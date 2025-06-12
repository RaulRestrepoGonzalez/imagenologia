from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Sistema de Imagenología"
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "imagenologia_db"
    secret_key: str = "supersecret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    mail_sender: str = "notificaciones@ips.com"

    class Config:
        env_file = ".env"

settings = Settings()