"""
Configuración de pytest y fixtures comunes para tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno para tests
load_dotenv()

# Configuración de base de datos de test
TEST_MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017")
TEST_DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "ips_imagenologia_test")

@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests asíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_database():
    """Crear base de datos de test"""
    client = AsyncIOMotorClient(TEST_MONGO_URI)
    db = client[TEST_DATABASE_NAME]
    
    # Limpiar base de datos antes de los tests
    await db.client.drop_database(TEST_DATABASE_NAME)
    
    yield db
    
    # Limpiar después de los tests
    await db.client.drop_database(TEST_DATABASE_NAME)
    client.close()

@pytest.fixture
async def test_client(test_database):
    """Crear cliente HTTP para tests"""
    # Mock de la base de datos para tests
    import sys
    import os
    
    # Agregar el directorio raíz al path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app import create_app
    from app.database import get_database
    
    # Crear aplicación de test
    app = create_app()
    
    # Mock de la base de datos
    app.dependency_overrides[get_database] = lambda: test_database
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_paciente_data():
    """Datos de ejemplo para un paciente"""
    return {
        "nombre": "Juan Carlos",
        "identificacion": "12345678",
        "email": "juan.carlos@test.com",
        "telefono": "+573001234567",
        "fecha_nacimiento": "1990-05-15T00:00:00",
        "direccion": "Calle 123 #45-67",
        "genero": "Masculino",
        "grupo_sanguineo": "O+",
        "alergias": "Ninguna",
        "condiciones_cronicas": "Ninguna",
        "medicamentos": "Ninguno"
    }

@pytest.fixture
def sample_estudio_data():
    """Datos de ejemplo para un estudio"""
    return {
        "paciente_id": "507f1f77bcf86cd799439011",  # ObjectId de ejemplo
        "tipo_estudio": "Radiografía de tórax",
        "medico_solicitante": "Dr. García",
        "prioridad": "normal",
        "indicaciones": "Dolor en el pecho",
        "sala": "Sala 1",
        "tecnico_asignado": "Técnico López"
    }

@pytest.fixture
def sample_cita_data():
    """Datos de ejemplo para una cita"""
    return {
        "estudio_id": "507f1f77bcf86cd799439012",  # ObjectId de ejemplo
        "fecha_hora": "2024-02-15T10:00:00",
        "tecnico_asignado": "Técnico López",
        "sala": "Sala 1",
        "duracion_minutos": 30,
        "observaciones": "Paciente con movilidad reducida"
    }

@pytest.fixture
def sample_informe_data():
    """Datos de ejemplo para un informe"""
    return {
        "estudio_id": "507f1f77bcf86cd799439012",  # ObjectId de ejemplo
        "medico_radiologo": "Dr. Rodríguez",
        "hallazgos": "Pulmones sin alteraciones radiológicas",
        "conclusion": "Radiografía de tórax normal",
        "recomendaciones": "Continuar con el tratamiento prescrito",
        "prioridad": "normal"
    }

@pytest.fixture
async def paciente_creado(test_client, sample_paciente_data):
    """Crear un paciente de prueba y retornarlo"""
    response = await test_client.post("/api/pacientes", json=sample_paciente_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
async def estudio_creado(test_client, sample_estudio_data, paciente_creado):
    """Crear un estudio de prueba y retornarlo"""
    # Usar el ID del paciente creado
    estudio_data = sample_estudio_data.copy()
    estudio_data["paciente_id"] = paciente_creado["id"]
    
    response = await test_client.post("/api/estudios", json=estudio_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
async def cita_creada(test_client, sample_cita_data, estudio_creado):
    """Crear una cita de prueba y retornarla"""
    # Usar el ID del estudio creado
    cita_data = sample_cita_data.copy()
    cita_data["estudio_id"] = estudio_creado["id"]
    
    response = await test_client.post("/api/citas", json=cita_data)
    assert response.status_code == 200
    return response.json()



