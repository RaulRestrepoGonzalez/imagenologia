"""
Tests para el módulo de citas
"""

import pytest
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, timedelta

class TestCitas:
    """Tests para el módulo de citas"""
    
    async def test_create_cita_success(self, test_client: AsyncClient, sample_cita_data, estudio_creado):
        """Test crear cita exitosamente"""
        # Usar el estudio creado
        cita_data = sample_cita_data.copy()
        cita_data["estudio_id"] = estudio_creado["id"]
        
        response = await test_client.post("/api/citas", json=cita_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se creó correctamente
        assert data["estudio_id"] == estudio_creado["id"]
        assert data["tecnico_asignado"] == cita_data["tecnico_asignado"]
        assert data["sala"] == cita_data["sala"]
        assert data["estado"] == "programada"
        assert "id" in data
        assert "fecha_creacion" in data
        assert "fecha_actualizacion" in data
    
    async def test_create_cita_estudio_not_found(self, test_client: AsyncClient, sample_cita_data):
        """Test crear cita con estudio que no existe"""
        cita_data = sample_cita_data.copy()
        cita_data["estudio_id"] = str(ObjectId())  # ID que no existe
        
        response = await test_client.post("/api/citas", json=cita_data)
        assert response.status_code == 404
        assert "estudio no encontrado" in response.json()["detail"].lower()
    
    async def test_create_cita_conflict_sala(self, test_client: AsyncClient, sample_cita_data, estudio_creado):
        """Test crear cita con conflicto de sala"""
        # Crear primera cita
        cita1_data = sample_cita_data.copy()
        cita1_data["estudio_id"] = estudio_creado["id"]
        cita1_data["fecha_hora"] = "2024-02-15T10:00:00"
        
        response1 = await test_client.post("/api/citas", json=cita1_data)
        assert response1.status_code == 200
        
        # Crear segundo estudio para la segunda cita
        estudio2_data = {
            "paciente_id": estudio_creado["paciente_id"],
            "tipo_estudio": "Ecografía abdominal",
            "medico_solicitante": "Dr. Martínez"
        }
        estudio2_response = await test_client.post("/api/estudios", json=estudio2_data)
        assert estudio2_response.status_code == 200
        
        # Intentar crear segunda cita con misma sala y horario
        cita2_data = sample_cita_data.copy()
        cita2_data["estudio_id"] = estudio2_response.json()["id"]
        cita2_data["fecha_hora"] = "2024-02-15T10:00:00"  # Mismo horario
        cita2_data["sala"] = cita1_data["sala"]  # Misma sala
        
        response2 = await test_client.post("/api/citas", json=cita2_data)
        assert response2.status_code == 400
        assert "conflicto de horario" in response.json()["detail"].lower()
    
    async def test_create_cita_conflict_tecnico(self, test_client: AsyncClient, sample_cita_data, estudio_creado):
        """Test crear cita con conflicto de técnico"""
        # Crear primera cita
        cita1_data = sample_cita_data.copy()
        cita1_data["estudio_id"] = estudio_creado["id"]
        cita1_data["fecha_hora"] = "2024-02-15T10:00:00"
        
        response1 = await test_client.post("/api/citas", json=cita1_data)
        assert response1.status_code == 200
        
        # Crear segundo estudio para la segunda cita
        estudio2_data = {
            "paciente_id": estudio_creado["paciente_id"],
            "tipo_estudio": "Ecografía abdominal",
            "medico_solicitante": "Dr. Martínez"
        }
        estudio2_response = await test_client.post("/api/estudios", json=estudio2_data)
        assert estudio2_response.status_code == 200
        
        # Intentar crear segunda cita con mismo técnico y horario
        cita2_data = sample_cita_data.copy()
        cita2_data["estudio_id"] = estudio2_response.json()["id"]
        cita2_data["fecha_hora"] = "2024-02-15T10:00:00"  # Mismo horario
        cita2_data["tecnico_asignado"] = cita1_data["tecnico_asignado"]  # Mismo técnico
        
        response2 = await test_client.post("/api/citas", json=cita2_data)
        assert response2.status_code == 400
        assert "conflicto de horario" in response.json()["detail"].lower()
    
    async def test_get_citas_list(self, test_client: AsyncClient, cita_creada):
        """Test obtener lista de citas"""
        response = await test_client.get("/api/citas")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verificar estructura de la primera cita
        if data:
            cita = data[0]
            assert "id" in cita
            assert "estudio_id" in cita
            assert "fecha_hora" in cita
            assert "tecnico_asignado" in cita
            assert "sala" in cita
    
    async def test_get_citas_with_filters(self, test_client: AsyncClient, cita_creada):
        """Test obtener citas con filtros"""
        # Filtrar por fecha
        fecha = cita_creada["fecha_hora"][:10]  # Solo la fecha
        response = await test_client.get(f"/api/citas?fecha={fecha}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Filtrar por estado
        response = await test_client.get("/api/citas?estado=programada")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert all(cita["estado"] == "programada" for cita in data)
    
    async def test_get_citas_pagination(self, test_client: AsyncClient, sample_cita_data, estudio_creado):
        """Test paginación de citas"""
        # Crear múltiples citas
        for i in range(15):
            cita_data = sample_cita_data.copy()
            cita_data["estudio_id"] = estudio_creado["id"]
            cita_data["fecha_hora"] = f"2024-02-{15+i:02d}T10:00:00"
            await test_client.post("/api/citas", json=cita_data)
        
        # Test con límite
        response = await test_client.get("/api/citas?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        
        # Test con skip
        response = await test_client.get("/api/citas?skip=10&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    async def test_get_cita_by_id(self, test_client: AsyncClient, cita_creada):
        """Test obtener cita por ID"""
        cita_id = cita_creada["id"]
        
        response = await test_client.get(f"/api/citas/{cita_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == cita_id
        assert data["estudio_id"] == cita_creada["estudio_id"]
        assert data["tecnico_asignado"] == cita_creada["tecnico_asignado"]
    
    async def test_get_cita_not_found(self, test_client: AsyncClient):
        """Test obtener cita que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.get(f"/api/citas/{fake_id}")
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    async def test_get_cita_invalid_id(self, test_client: AsyncClient):
        """Test obtener cita con ID inválido"""
        response = await test_client.get("/api/citas/invalid-id")
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_get_citas_estudio(self, test_client: AsyncClient, cita_creada):
        """Test obtener citas de un estudio específico"""
        estudio_id = cita_creada["estudio_id"]
        
        response = await test_client.get(f"/api/estudios/{estudio_id}/citas")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(cita["estudio_id"] == estudio_id for cita in data)
    
    async def test_get_citas_estudio_not_found(self, test_client: AsyncClient):
        """Test obtener citas de estudio que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.get(f"/api/estudios/{fake_id}/citas")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    async def test_update_cita_success(self, test_client: AsyncClient, cita_creada):
        """Test actualizar cita exitosamente"""
        cita_id = cita_creada["id"]
        
        update_data = {
            "fecha_hora": "2024-02-16T14:00:00",
            "observaciones": "Cita reprogramada"
        }
        
        response = await test_client.put(f"/api/citas/{cita_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["fecha_hora"] == update_data["fecha_hora"]
        assert data["observaciones"] == update_data["observaciones"]
        assert data["fecha_actualizacion"] != cita_creada["fecha_actualizacion"]
    
    async def test_update_cita_not_found(self, test_client: AsyncClient):
        """Test actualizar cita que no existe"""
        fake_id = str(ObjectId())
        update_data = {"fecha_hora": "2024-02-16T14:00:00"}
        
        response = await test_client.put(f"/api/citas/{fake_id}", json=update_data)
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    async def test_update_cita_invalid_id(self, test_client: AsyncClient):
        """Test actualizar cita con ID inválido"""
        update_data = {"fecha_hora": "2024-02-16T14:00:00"}
        
        response = await test_client.put("/api/citas/invalid-id", json=update_data)
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_update_cita_conflict(self, test_client: AsyncClient, cita_creada, estudio_creado):
        """Test actualizar cita con conflicto de horario"""
        cita_id = cita_creada["id"]
        
        # Crear otra cita en el mismo horario
        cita2_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "2024-02-15T10:00:00",
            "tecnico_asignado": "Técnico Pérez",
            "sala": "Sala 2"
        }
        cita2_response = await test_client.post("/api/citas", json=cita2_data)
        assert cita2_response.status_code == 200
        
        # Intentar actualizar la primera cita al mismo horario y sala de la segunda
        update_data = {
            "fecha_hora": "2024-02-15T10:00:00",
            "sala": "Sala 2"
        }
        
        response = await test_client.put(f"/api/citas/{cita_id}", json=update_data)
        assert response.status_code == 400
        assert "conflicto de horario" in response.json()["detail"].lower()
    
    async def test_update_cita_no_data(self, test_client: AsyncClient, cita_creada):
        """Test actualizar cita sin datos"""
        cita_id = cita_creada["id"]
        
        response = await test_client.put(f"/api/citas/{cita_id}", json={})
        assert response.status_code == 400
        assert "no se proporcionaron datos" in response.json()["detail"].lower()
    
    async def test_delete_cita_success(self, test_client: AsyncClient, cita_creada):
        """Test cancelar cita exitosamente"""
        cita_id = cita_creada["id"]
        
        response = await test_client.delete(f"/api/citas/{cita_id}")
        assert response.status_code == 200
        assert "cancelada" in response.json()["message"].lower()
    
    async def test_delete_cita_not_found(self, test_client: AsyncClient):
        """Test cancelar cita que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.delete(f"/api/citas/{fake_id}")
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    async def test_delete_cita_invalid_id(self, test_client: AsyncClient):
        """Test cancelar cita con ID inválido"""
        response = await test_client.delete("/api/citas/invalid-id")
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_update_asistencia_cita(self, test_client: AsyncClient, cita_creada):
        """Test actualizar asistencia de cita"""
        cita_id = cita_creada["id"]
        
        # Actualizar asistencia
        response = await test_client.put(f"/api/citas/{cita_id}/asistencia?asistio=true")
        assert response.status_code == 200
        assert "actualizada" in response.json()["message"].lower()
        
        # Verificar que la cita se actualizó
        get_response = await test_client.get(f"/api/citas/{cita_id}")
        assert get_response.status_code == 200
        cita_data = get_response.json()
        assert cita_data["asistio"] is True
    
    async def test_update_asistencia_cita_not_found(self, test_client: AsyncClient):
        """Test actualizar asistencia de cita que no existe"""
        fake_id = str(ObjectId())
        
        response = await test_client.put(f"/api/citas/{fake_id}/asistencia?asistio=true")
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    async def test_update_asistencia_cita_invalid_id(self, test_client: AsyncClient):
        """Test actualizar asistencia de cita con ID inválido"""
        response = await test_client.put("/api/citas/invalid-id/asistencia?asistio=true")
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_cita_data_validation(self, test_client: AsyncClient, estudio_creado):
        """Test validación de datos de cita"""
        # Fecha inválida
        invalid_date_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "fecha-invalida",
            "tecnico_asignado": "Técnico López",
            "sala": "Sala 1"
        }
        
        response = await test_client.post("/api/citas", json=invalid_date_data)
        assert response.status_code == 422
        
        # Campos requeridos faltantes
        incomplete_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "2024-02-15T10:00:00"
            # Faltan campos requeridos
        }
        
        response = await test_client.post("/api/citas", json=incomplete_data)
        assert response.status_code == 422



