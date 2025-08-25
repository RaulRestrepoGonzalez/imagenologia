"""
Tests para el módulo de pacientes
"""

import pytest
from httpx import AsyncClient
from bson import ObjectId

class TestPacientes:
    """Tests para el módulo de pacientes"""
    
    async def test_create_paciente_success(self, test_client: AsyncClient, sample_paciente_data):
        """Test crear paciente exitosamente"""
        response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se creó correctamente
        assert data["nombre"] == sample_paciente_data["nombre"]
        assert data["identificacion"] == sample_paciente_data["identificacion"]
        assert data["email"] == sample_paciente_data["email"]
        assert "id" in data
        assert "fecha_creacion" in data
        assert "fecha_actualizacion" in data
    
    async def test_create_paciente_duplicate_identificacion(self, test_client: AsyncClient, sample_paciente_data):
        """Test crear paciente con identificación duplicada"""
        # Crear primer paciente
        response1 = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert response1.status_code == 200
        
        # Intentar crear segundo paciente con misma identificación
        response2 = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert response2.status_code == 400
        assert "identificación" in response2.json()["detail"].lower()
    
    async def test_create_paciente_duplicate_email(self, test_client: AsyncClient, sample_paciente_data):
        """Test crear paciente con email duplicado"""
        # Crear primer paciente
        response1 = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert response1.status_code == 200
        
        # Crear segundo paciente con email duplicado pero identificación diferente
        paciente2 = sample_paciente_data.copy()
        paciente2["identificacion"] = "87654321"
        
        response2 = await test_client.post("/api/pacientes", json=paciente2)
        assert response2.status_code == 400
        assert "email" in response2.json()["detail"].lower()
    
    async def test_create_paciente_invalid_data(self, test_client: AsyncClient):
        """Test crear paciente con datos inválidos"""
        # Paciente sin campos requeridos
        invalid_data = {
            "nombre": "Juan",
            "email": "juan@test.com"
            # Faltan campos requeridos
        }
        
        response = await test_client.post("/api/pacientes", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    async def test_get_pacientes_list(self, test_client: AsyncClient, sample_paciente_data):
        """Test obtener lista de pacientes"""
        # Crear un paciente primero
        await test_client.post("/api/pacientes", json=sample_paciente_data)
        
        # Obtener lista
        response = await test_client.get("/api/pacientes")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verificar estructura del primer paciente
        if data:
            paciente = data[0]
            assert "id" in paciente
            assert "nombre" in paciente
            assert "identificacion" in paciente
            assert "email" in paciente
    
    async def test_get_pacientes_pagination(self, test_client: AsyncClient, sample_paciente_data):
        """Test paginación de pacientes"""
        # Crear múltiples pacientes
        for i in range(15):
            paciente = sample_paciente_data.copy()
            paciente["identificacion"] = f"1234567{i:02d}"
            paciente["email"] = f"paciente{i}@test.com"
            await test_client.post("/api/pacientes", json=paciente)
        
        # Test con límite
        response = await test_client.get("/api/pacientes?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        
        # Test con skip
        response = await test_client.get("/api/pacientes?skip=10&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    async def test_get_paciente_by_id(self, test_client: AsyncClient, sample_paciente_data):
        """Test obtener paciente por ID"""
        # Crear paciente
        create_response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert create_response.status_code == 200
        
        paciente_id = create_response.json()["id"]
        
        # Obtener paciente por ID
        response = await test_client.get(f"/api/pacientes/{paciente_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == paciente_id
        assert data["nombre"] == sample_paciente_data["nombre"]
        assert data["identificacion"] == sample_paciente_data["identificacion"]
    
    async def test_get_paciente_invalid_id(self, test_client: AsyncClient):
        """Test obtener paciente con ID inválido"""
        # ID inválido
        response = await test_client.get("/api/pacientes/invalid-id")
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_get_paciente_not_found(self, test_client: AsyncClient):
        """Test obtener paciente que no existe"""
        # ID válido pero que no existe
        fake_id = str(ObjectId())
        response = await test_client.get(f"/api/pacientes/{fake_id}")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    async def test_update_paciente_success(self, test_client: AsyncClient, sample_paciente_data):
        """Test actualizar paciente exitosamente"""
        # Crear paciente
        create_response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert create_response.status_code == 200
        
        paciente_id = create_response.json()["id"]
        
        # Actualizar datos
        update_data = {
            "nombre": "Juan Carlos Actualizado",
            "telefono": "+573009876543"
        }
        
        response = await test_client.put(f"/api/pacientes/{paciente_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nombre"] == update_data["nombre"]
        assert data["telefono"] == update_data["telefono"]
        assert data["identificacion"] == sample_paciente_data["identificacion"]  # No cambió
    
    async def test_update_paciente_not_found(self, test_client: AsyncClient):
        """Test actualizar paciente que no existe"""
        fake_id = str(ObjectId())
        update_data = {"nombre": "Nuevo Nombre"}
        
        response = await test_client.put(f"/api/pacientes/{fake_id}", json=update_data)
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    async def test_update_paciente_invalid_id(self, test_client: AsyncClient):
        """Test actualizar paciente con ID inválido"""
        update_data = {"nombre": "Nuevo Nombre"}
        
        response = await test_client.put("/api/pacientes/invalid-id", json=update_data)
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_update_paciente_duplicate_identificacion(self, test_client: AsyncClient, sample_paciente_data):
        """Test actualizar paciente con identificación duplicada"""
        # Crear dos pacientes
        paciente1 = sample_paciente_data.copy()
        paciente2 = sample_paciente_data.copy()
        paciente2["identificacion"] = "87654321"
        paciente2["email"] = "paciente2@test.com"
        
        response1 = await test_client.post("/api/pacientes", json=paciente1)
        response2 = await test_client.post("/api/pacientes", json=paciente2)
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Intentar actualizar el segundo paciente con la identificación del primero
        paciente2_id = response2.json()["id"]
        update_data = {"identificacion": paciente1["identificacion"]}
        
        response = await test_client.put(f"/api/pacientes/{paciente2_id}", json=update_data)
        assert response.status_code == 400
        assert "identificación" in response.json()["detail"].lower()
    
    async def test_update_paciente_no_data(self, test_client: AsyncClient, sample_paciente_data):
        """Test actualizar paciente sin datos"""
        # Crear paciente
        create_response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert create_response.status_code == 200
        
        paciente_id = create_response.json()["id"]
        
        # Intentar actualizar sin datos
        response = await test_client.put(f"/api/pacientes/{paciente_id}", json={})
        assert response.status_code == 400
        assert "no se proporcionaron datos" in response.json()["detail"].lower()
    
    async def test_delete_paciente_success(self, test_client: AsyncClient, sample_paciente_data):
        """Test eliminar paciente exitosamente (soft delete)"""
        # Crear paciente
        create_response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert create_response.status_code == 200
        
        paciente_id = create_response.json()["id"]
        
        # Eliminar paciente
        response = await test_client.delete(f"/api/pacientes/{paciente_id}")
        assert response.status_code == 200
        assert "inactivo" in response.json()["message"].lower()
    
    async def test_delete_paciente_not_found(self, test_client: AsyncClient):
        """Test eliminar paciente que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.delete(f"/api/pacientes/{fake_id}")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    async def test_delete_paciente_invalid_id(self, test_client: AsyncClient):
        """Test eliminar paciente con ID inválido"""
        response = await test_client.delete("/api/pacientes/invalid-id")
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_get_estudios_paciente(self, test_client: AsyncClient, sample_paciente_data, sample_estudio_data):
        """Test obtener estudios de un paciente"""
        # Crear paciente
        paciente_response = await test_client.post("/api/pacientes", json=sample_paciente_data)
        assert paciente_response.status_code == 200
        
        paciente_id = paciente_response.json()["id"]
        
        # Crear estudio para el paciente
        estudio_data = sample_estudio_data.copy()
        estudio_data["paciente_id"] = paciente_id
        
        estudio_response = await test_client.post("/api/estudios", json=estudio_data)
        assert estudio_response.status_code == 200
        
        # Obtener estudios del paciente
        response = await test_client.get(f"/api/pacientes/{paciente_id}/estudios")
        assert response.status_code == 200
        
        data = response.json()
        assert "paciente" in data
        assert "estudios" in data
        assert len(data["estudios"]) >= 1
        assert data["estudios"][0]["paciente_id"] == paciente_id
    
    async def test_get_estudios_paciente_not_found(self, test_client: AsyncClient):
        """Test obtener estudios de paciente que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.get(f"/api/pacientes/{fake_id}/estudios")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    async def test_paciente_data_validation(self, test_client: AsyncClient):
        """Test validación de datos del paciente"""
        # Email inválido
        invalid_email_data = sample_paciente_data.copy()
        invalid_email_data["email"] = "email-invalido"
        
        response = await test_client.post("/api/pacientes", json=invalid_email_data)
        assert response.status_code == 422
        
        # Teléfono inválido
        invalid_phone_data = sample_paciente_data.copy()
        invalid_phone_data["telefono"] = "123"
        
        response = await test_client.post("/api/pacientes", json=invalid_phone_data)
        assert response.status_code == 422
        
        # Fecha de nacimiento inválida
        invalid_date_data = sample_paciente_data.copy()
        invalid_date_data["fecha_nacimiento"] = "fecha-invalida"
        
        response = await test_client.post("/api/pacientes", json=invalid_date_data)
        assert response.status_code == 422



