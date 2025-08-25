"""
Configuración del servidor para la aplicación
"""

import os
from typing import Dict, Any

class ServerConfig:
    """Configuración del servidor"""
    
    def __init__(self):
        # Configuración básica
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Configuración de desarrollo
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.reload = os.getenv("RELOAD", "True").lower() == "true"
        self.workers = int(os.getenv("WORKERS", "1"))
        
        # Configuración de logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE")
        
        # Configuración de CORS
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
        
        # Configuración de base de datos
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "ips_imagenologia")
        
        # Configuración de seguridad
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # Configuración de servicios
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        self.sms_provider = os.getenv("SMS_PROVIDER", "twilio")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        # Configuración de archivos DICOM
        self.dicom_storage_path = os.getenv("DICOM_STORAGE_PATH", "./uploads/dicom")
        self.dicom_processed_path = os.getenv("DICOM_PROCESSED_PATH", "./processed/dicom")
        self.dicom_max_file_size = os.getenv("DICOM_MAX_FILE_SIZE", "100MB")
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Obtener configuración para Uvicorn"""
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload and self.debug,
            "log_level": self.log_level.lower(),
            "workers": self.workers if not self.debug else 1,
            "access_log": True,
            "use_colors": True
        }
    
    def is_production(self) -> bool:
        """Verificar si está en producción"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Verificar si está en desarrollo"""
        return self.environment.lower() == "development"
    
    def validate_config(self) -> bool:
        """Validar configuración mínima"""
        errors = []
        
        if not self.secret_key or self.secret_key == "dev-secret-key-change-in-production":
            if self.is_production():
                errors.append("SECRET_KEY debe ser configurada en producción")
        
        if not self.smtp_username or not self.smtp_password:
            errors.append("Configuración SMTP incompleta")
        
        if self.sms_provider == "twilio" and not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            errors.append("Configuración de Twilio incompleta")
        
        if errors:
            for error in errors:
                print(f"⚠️  {error}")
            return False
        
        return True

# Instancia global de configuración
config = ServerConfig()



