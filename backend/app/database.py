from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)# Conectar a MongoDB usando la URI definida en settings
db = client[settings.database_name]#poner el nombre de la base de datos
