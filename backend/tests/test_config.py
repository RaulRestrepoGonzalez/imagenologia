"""
Configuración específica para tests
"""

import os

# Configuración de base de datos para tests
TEST_MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017")
TEST_DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "ips_imagenologia_test")

# Configuración de la aplicación para tests
TEST_DEBUG = True
TEST_LOG_LEVEL = "DEBUG"

# Configuración de servicios para tests
TEST_SMTP_SERVER = "smtp.gmail.com"
TEST_SMTP_PORT = 587
TEST_SMTP_USERNAME = "test@example.com"
TEST_SMTP_PASSWORD = "test-password"

TEST_SMS_PROVIDER = "generic"
TEST_SMS_API_URL = "http://localhost:8001/sms"
TEST_SMS_API_KEY = "test-api-key"

# Configuración de timeouts para tests
TEST_TIMEOUT = 30  # segundos
TEST_RETRY_ATTEMPTS = 3



