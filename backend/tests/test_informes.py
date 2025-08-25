"""
Tests para el módulo de informes
"""

import pytest
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, timedelta

class TestInformes:
    """Tests para el módulo de informes"""
    
    async def test_get_estadisticas_success(self, test_client: AsyncClient, estudio_creado):
        """Test obtener estadísticas exitosamente"""
        # Crear algunas citas para generar estadísticas
        cita_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "2024-02-15T10:00:00",
            "tecnico_asignado": "Técnico López",
            "sala": "Sala 1"
        }
        await test_client.post("/api/citas", json=cita_data)
        
        # Obtener estadísticas
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        assert "estudios_por_estado" in data
        assert "estudios_por_tipo" in data
        assert "citas_por_estado" in data
        assert "tasa_asistencia" in data
    
    async def test_get_estadisticas_invalid_dates(self, test_client: AsyncClient):
        """Test obtener estadísticas con fechas inválidas"""
        # Fecha inválida
        response = await test_client.get("/api/informes/estadisticas?inicio=fecha-invalida&fin=2024-02-29")
        assert response.status_code == 400
        
        # Fecha de inicio mayor que fecha fin
        response = await test_client.get("/api/informes/estadisticas?inicio=2024-02-29&fin=2024-02-01")
        assert response.status_code == 400
    
    async def test_get_estadisticas_missing_dates(self, test_client: AsyncClient):
        """Test obtener estadísticas sin fechas"""
        response = await test_client.get("/api/informes/estadisticas")
        assert response.status_code == 422  # Validation error
    
    async def test_estadisticas_estudios_por_estado(self, test_client: AsyncClient, estudio_creado):
        """Test estadísticas de estudios por estado"""
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        estudios_por_estado = data["estudios_por_estado"]
        
        # Verificar que hay al menos un estudio
        assert len(estudios_por_estado) >= 1
        
        # Verificar estructura de los datos
        for estadistica in estudios_por_estado:
            assert "estado" in estadistica
            assert "cantidad" in estadistica
            assert isinstance(estadistica["cantidad"], int)
    
    async def test_estadisticas_estudios_por_tipo(self, test_client: AsyncClient, estudio_creado):
        """Test estadísticas de estudios por tipo"""
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        estudios_por_tipo = data["estudios_por_tipo"]
        
        # Verificar que hay al menos un tipo de estudio
        assert len(estudios_por_tipo) >= 1
        
        # Verificar estructura de los datos
        for estadistica in estudios_por_tipo:
            assert "tipo_estudio" in estadistica
            assert "cantidad" in estadistica
            assert isinstance(estadistica["cantidad"], int)
    
    async def test_estadisticas_citas_por_estado(self, test_client: AsyncClient, estudio_creado):
        """Test estadísticas de citas por estado"""
        # Crear cita
        cita_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "2024-02-15T10:00:00",
            "tecnico_asignado": "Técnico López",
            "sala": "Sala 1"
        }
        await test_client.post("/api/citas", json=cita_data)
        
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        citas_por_estado = data["citas_por_estado"]
        
        # Verificar que hay al menos un estado de cita
        assert len(citas_por_estado) >= 1
        
        # Verificar estructura de los datos
        for estadistica in citas_por_estado:
            assert "estado" in estadistica
            assert "cantidad" in estadistica
            assert isinstance(estadistica["cantidad"], int)
    
    async def test_estadisticas_tasa_asistencia(self, test_client: AsyncClient, estudio_creado):
        """Test estadísticas de tasa de asistencia"""
        # Crear cita
        cita_data = {
            "estudio_id": estudio_creado["id"],
            "fecha_hora": "2024-02-15T10:00:00",
            "tecnico_asignado": "Técnico López",
            "sala": "Sala 1"
        }
        cita_response = await test_client.post("/api/citas", json=cita_data)
        assert cita_response.status_code == 200
        
        # Marcar asistencia
        cita_id = cita_response.json()["id"]
        await test_client.put(f"/api/citas/{cita_id}/asistencia?asistio=true")
        
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        tasa_asistencia = data["tasa_asistencia"]
        
        # Verificar estructura de los datos
        assert "total_citas" in tasa_asistencia
        assert "citas_asistidas" in tasa_asistencia
        assert "porcentaje_asistencia" in tasa_asistencia
        assert isinstance(tasa_asistencia["total_citas"], int)
        assert isinstance(tasa_asistencia["citas_asistidas"], int)
        assert isinstance(tasa_asistencia["porcentaje_asistencia"], (int, float))
    
    async def test_estadisticas_rango_fechas_vacio(self, test_client: AsyncClient):
        """Test estadísticas con rango de fechas sin datos"""
        fecha_inicio = "2020-01-01"
        fecha_fin = "2020-01-31"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar que se retornan estructuras vacías
        assert data["estudios_por_estado"] == []
        assert data["estudios_por_tipo"] == []
        assert data["citas_por_estado"] == []
        assert data["tasa_asistencia"]["total_citas"] == 0
        assert data["tasa_asistencia"]["citas_asistidas"] == 0
        assert data["tasa_asistencia"]["porcentaje_asistencia"] == 0
    
    async def test_estadisticas_formato_fecha_invalido(self, test_client: AsyncClient):
        """Test estadísticas con formato de fecha inválido"""
        # Formato de fecha incorrecto
        response = await test_client.get("/api/informes/estadisticas?inicio=2024/02/01&fin=2024/02/29")
        assert response.status_code == 400
        
        # Fecha con formato incorrecto
        response = await test_client.get("/api/informes/estadisticas?inicio=01-02-2024&fin=29-02-2024")
        assert response.status_code == 400
    
    async def test_estadisticas_fechas_futuras(self, test_client: AsyncClient):
        """Test estadísticas con fechas futuras"""
        fecha_futura = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        fecha_fin_futura = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_futura}&fin={fecha_fin_futura}")
        assert response.status_code == 200
        
        data = response.json()
        # Debería retornar datos vacíos para fechas futuras
        assert data["estudios_por_estado"] == []
        assert data["estudios_por_tipo"] == []
        assert data["citas_por_estado"] == []
    
    async def test_estadisticas_ordenamiento(self, test_client: AsyncClient, estudio_creado):
        """Test que las estadísticas estén ordenadas correctamente"""
        # Crear múltiples estudios para verificar ordenamiento
        for i in range(5):
            estudio_data = {
                "paciente_id": estudio_creado["paciente_id"],
                "tipo_estudio": f"Estudio {i}",
                "medico_solicitante": f"Dr. {i}"
            }
            await test_client.post("/api/estudios", json=estudio_data)
        
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        estudios_por_tipo = data["estudios_por_tipo"]
        
        # Verificar que está ordenado por cantidad (descendente)
        cantidades = [est["cantidad"] for est in estudios_por_tipo]
        assert cantidades == sorted(cantidades, reverse=True)
    
    async def test_estadisticas_agregacion_correcta(self, test_client: AsyncClient, estudio_creado):
        """Test que la agregación de estadísticas sea correcta"""
        # Crear múltiples estudios del mismo tipo
        for i in range(3):
            estudio_data = {
                "paciente_id": estudio_creado["paciente_id"],
                "tipo_estudio": "Radiografía de tórax",  # Mismo tipo
                "medico_solicitante": f"Dr. {i}"
            }
            await test_client.post("/api/estudios", json=estudio_data)
        
        fecha_inicio = "2024-02-01"
        fecha_fin = "2024-02-29"
        
        response = await test_client.get(f"/api/informes/estadisticas?inicio={fecha_inicio}&fin={fecha_fin}")
        assert response.status_code == 200
        
        data = response.json()
        estudios_por_tipo = data["estudios_por_tipo"]
        
        # Buscar el tipo de estudio específico
        radiografia_estadistica = None
        for estadistica in estudios_por_tipo:
            if estadistica["tipo_estudio"] == "Radiografía de tórax":
                radiografia_estadistica = estadistica
                break
        
        # Verificar que se agregó correctamente (debería ser 4: 1 original + 3 nuevos)
        assert radiografia_estadistica is not None
        assert radiografia_estadistica["cantidad"] == 4



