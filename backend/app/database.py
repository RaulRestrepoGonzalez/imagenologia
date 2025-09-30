from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "imagenologia")

# Cliente MongoDB
client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]

# Alias para compatibilidad
db = database

def get_database():
    """Obtener instancia de la base de datos"""
    return database

def object_id_to_str(obj):
    """Convertir ObjectId a string para serialización JSON"""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def init_database():
    """Inicializar la base de datos con índices y configuración"""
    try:
        db = get_database()
        
        # Crear índices para mejor rendimiento
        await db.pacientes.create_index("identificacion", unique=True)
        await db.pacientes.create_index("email")
        await db.pacientes.create_index("fecha_creacion")
        
        await db.estudios.create_index("paciente_id")
        await db.estudios.create_index("estado")
        await db.estudios.create_index("fecha_solicitud")
        await db.estudios.create_index("tipo_estudio")
        await db.estudios.create_index("medico_solicitante")
        
        await db.citas.create_index("estudio_id")
        await db.citas.create_index("fecha_hora")
        await db.citas.create_index("estado")
        await db.citas.create_index("tecnico_asignado")
        await db.citas.create_index("sala")
        
        await db.informes.create_index("estudio_id")
        await db.informes.create_index("medico_radiologo")
        await db.informes.create_index("fecha_creacion")
        await db.informes.create_index("firmado")
        
        await db.notificaciones.create_index("paciente_id")
        await db.notificaciones.create_index("estudio_id")
        await db.notificaciones.create_index("tipo")
        await db.notificaciones.create_index("enviada")
        await db.notificaciones.create_index("fecha_creacion")
        
        # Índices para archivos DICOM
        await db.dicom_files.create_index("estudio_id")
        await db.dicom_files.create_index("paciente_id")
        await db.dicom_files.create_index("fecha_subida")
        
        logging.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logging.error(f"Error inicializando base de datos: {str(e)}")
        raise

async def close_database():
    """Cerrar conexión a la base de datos"""
    try:
        client.close()
        logging.info("Conexión a la base de datos cerrada")
    except Exception as e:
        logging.error(f"Error cerrando conexión a la base de datos: {str(e)}")

# Verificar conexión
async def test_connection():
    """Probar conexión a la base de datos"""
    try:
        await client.admin.command('ping')
        logging.info("Conexión a MongoDB exitosa")
        return True
    except Exception as e:
        logging.error(f"Error conectando a MongoDB: {str(e)}")
        return False