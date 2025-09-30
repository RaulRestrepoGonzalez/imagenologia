#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de los filtros en el módulo de citas
Este script ayuda a diagnosticar y validar que los filtros funcionen correctamente
tanto en el backend como en la integración con el frontend.
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Agregar el directorio backend al path para importar módulos
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.database import get_database
    from bson import ObjectId
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    print(
        "Asegúrate de estar en el directorio correcto y tener las dependencias instaladas"
    )
    sys.exit(1)

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Datos de prueba
TEST_PATIENTS = [
    {
        "nombre": "Juan Carlos",
        "apellidos": "Pérez González",
        "identificacion": "TEST12345678",
        "email": "juan.perez@test.com",
        "telefono": "3001234567",
        "fecha_nacimiento": "1985-05-15T00:00:00",
    },
    {
        "nombre": "María Fernanda",
        "apellidos": "García López",
        "identificacion": "TEST87654321",
        "email": "maria.garcia@test.com",
        "telefono": "3007654321",
        "fecha_nacimiento": "1990-08-22T00:00:00",
    },
    {
        "nombre": "Carlos Alberto",
        "apellidos": "Rodríguez Silva",
        "identificacion": "TEST11223344",
        "email": "carlos.rodriguez@test.com",
        "telefono": "3009876543",
        "fecha_nacimiento": "1975-12-10T00:00:00",
    },
]

TEST_APPOINTMENTS = [
    {
        "tipo_estudio": "Radiografía",
        "tipo_cita": "Consulta General",
        "estado": "programada",
        "observaciones": "Radiografía de tórax",
        "fecha_offset_hours": 2,  # 2 horas desde ahora
    },
    {
        "tipo_estudio": "Ecografía",
        "tipo_cita": "Control",
        "estado": "confirmada",
        "observaciones": "Ecografía abdominal de control",
        "fecha_offset_hours": 24,  # Mañana
    },
    {
        "tipo_estudio": "Tomografía",
        "tipo_cita": "Urgente",
        "estado": "en_proceso",
        "observaciones": "TAC de cráneo urgente",
        "fecha_offset_hours": -2,  # Hace 2 horas
    },
    {
        "tipo_estudio": "Resonancia Magnética",
        "tipo_cita": "Especialista",
        "estado": "completada",
        "observaciones": "RM de rodilla",
        "fecha_offset_hours": -48,  # Hace 2 días
    },
    {
        "tipo_estudio": "Mamografía",
        "tipo_cita": "Seguimiento",
        "estado": "cancelada",
        "observaciones": "Mamografía de seguimiento",
        "fecha_offset_hours": 72,  # En 3 días
    },
]


class CitasFilterTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_patients = []
        self.test_appointments = []

    async def setup_database(self):
        """Configurar datos de prueba en la base de datos"""
        print("🔧 Configurando datos de prueba en la base de datos...")

        db = get_database()

        # Limpiar datos de prueba anteriores
        await db.pacientes.delete_many({"identificacion": {"$regex": "^TEST"}})
        await db.citas.delete_many({"observaciones": {"$regex": "TEST:"}})

        # Crear pacientes de prueba
        for patient_data in TEST_PATIENTS:
            result = await db.pacientes.insert_one(patient_data)
            patient_data["_id"] = result.inserted_id
            self.test_patients.append(patient_data)

        print(f"✅ Creados {len(self.test_patients)} pacientes de prueba")

        # Crear citas de prueba
        base_time = datetime.now()
        for i, appointment_data in enumerate(TEST_APPOINTMENTS):
            patient = self.test_patients[i % len(self.test_patients)]

            cita_data = {
                "paciente_id": str(patient["_id"]),
                "fecha_cita": base_time
                + timedelta(hours=appointment_data["fecha_offset_hours"]),
                "tipo_estudio": appointment_data["tipo_estudio"],
                "tipo_cita": appointment_data["tipo_cita"],
                "estado": appointment_data["estado"],
                "observaciones": f"TEST: {appointment_data['observaciones']}",
                "fecha_creacion": datetime.now(),
                "fecha_actualizacion": datetime.now(),
            }

            result = await db.citas.insert_one(cita_data)
            cita_data["_id"] = result.inserted_id
            self.test_appointments.append(cita_data)

        print(f"✅ Creadas {len(self.test_appointments)} citas de prueba")

    def authenticate(self):
        """Autenticarse para obtener token"""
        print("🔐 Autenticando usuario...")

        login_data = {"email": "admin@imagenologia.com", "password": "admin123"}

        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )
                print("✅ Autenticación exitosa")
                return True
            else:
                print(f"❌ Error de autenticación: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando al API: {e}")
            return False

    def test_no_filters(self):
        """Probar obtener todas las citas sin filtros"""
        print("\n📋 Prueba 1: Obtener todas las citas (sin filtros)")

        response = self.session.get(f"{API_BASE}/citas")

        if response.status_code == 200:
            citas = response.json()
            print(f"✅ Se obtuvieron {len(citas)} citas")

            # Verificar que nuestras citas de prueba estén incluidas
            test_citas = [
                c for c in citas if c.get("observaciones", "").startswith("TEST:")
            ]
            print(f"✅ Citas de prueba encontradas: {len(test_citas)}")

            return len(test_citas) > 0
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False

    def test_filter_by_estado(self):
        """Probar filtro por estado"""
        print("\n📊 Prueba 2: Filtro por estado")

        estados_test = ["Programada", "Confirmada", "En Proceso", "Completada"]

        for estado in estados_test:
            print(f"  🔍 Probando estado: {estado}")

            params = {"estado": estado}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 200:
                citas = response.json()

                # Verificar que todas las citas tengan el estado correcto
                estados_incorrectos = [c for c in citas if c["estado"] != estado]

                if len(estados_incorrectos) == 0:
                    print(f"    ✅ {len(citas)} citas con estado '{estado}'")
                else:
                    print(
                        f"    ❌ {len(estados_incorrectos)} citas con estado incorrecto"
                    )
                    return False
            else:
                print(f"    ❌ Error: {response.status_code}")
                return False

        return True

    def test_filter_by_tipo_estudio(self):
        """Probar filtro por tipo de estudio"""
        print("\n🏥 Prueba 3: Filtro por tipo de estudio")

        tipos_test = ["Radiografía", "Ecografía", "Tomografía"]

        for tipo in tipos_test:
            print(f"  🔍 Probando tipo: {tipo}")

            params = {"tipo_estudio": tipo}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 200:
                citas = response.json()

                # Verificar que todas las citas tengan el tipo correcto
                tipos_incorrectos = [
                    c for c in citas if tipo.lower() not in c["tipo_estudio"].lower()
                ]

                if len(tipos_incorrectos) == 0:
                    print(f"    ✅ {len(citas)} citas con tipo '{tipo}'")
                else:
                    print(f"    ❌ {len(tipos_incorrectos)} citas con tipo incorrecto")
                    return False
            else:
                print(f"    ❌ Error: {response.status_code}")
                return False

        return True

    def test_filter_by_fecha(self):
        """Probar filtro por fecha"""
        print("\n📅 Prueba 4: Filtro por fecha")

        # Probar fecha de hoy
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"  🔍 Probando fecha de hoy: {today}")

        params = {"fecha": today}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas = response.json()
            print(f"    ✅ {len(citas)} citas para hoy")

            # Verificar que todas las citas sean de hoy
            for cita in citas:
                fecha_cita = datetime.fromisoformat(
                    cita["fecha_cita"].replace("Z", "+00:00")
                )
                if fecha_cita.date() != datetime.now().date():
                    print(f"    ❌ Cita con fecha incorrecta: {cita['fecha_cita']}")
                    return False

            return True
        else:
            print(f"    ❌ Error: {response.status_code}")
            return False

    def test_filter_by_paciente_nombre(self):
        """Probar filtro por nombre de paciente"""
        print("\n👤 Prueba 5: Filtro por nombre de paciente")

        nombres_test = ["Juan", "María", "Carlos"]

        for nombre in nombres_test:
            print(f"  🔍 Probando nombre: {nombre}")

            params = {"paciente_nombre": nombre}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 200:
                citas = response.json()

                # Verificar que todas las citas contengan el nombre
                nombres_incorrectos = []
                for cita in citas:
                    nombre_completo = f"{cita.get('paciente_nombre', '')} {cita.get('paciente_apellidos', '')}".lower()
                    if nombre.lower() not in nombre_completo:
                        nombres_incorrectos.append(cita)

                if len(nombres_incorrectos) == 0:
                    print(f"    ✅ {len(citas)} citas con nombre '{nombre}'")
                else:
                    print(
                        f"    ❌ {len(nombres_incorrectos)} citas sin el nombre buscado"
                    )
                    return False
            else:
                print(f"    ❌ Error: {response.status_code}")
                return False

        return True

    def test_combined_filters(self):
        """Probar combinación de filtros"""
        print("\n🔄 Prueba 6: Filtros combinados")

        # Combinar estado + tipo de estudio
        params = {"estado": "Programada", "tipo_estudio": "Radiografía"}

        print(f"  🔍 Probando: Estado='Programada' + Tipo='Radiografía'")

        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas = response.json()

            # Verificar que todas las citas cumplan ambos criterios
            for cita in citas:
                if cita["estado"] != "Programada":
                    print(f"    ❌ Estado incorrecto: {cita['estado']}")
                    return False
                if "radiografía" not in cita["tipo_estudio"].lower():
                    print(f"    ❌ Tipo incorrecto: {cita['tipo_estudio']}")
                    return False

            print(f"    ✅ {len(citas)} citas que cumplen ambos criterios")
            return True
        else:
            print(f"    ❌ Error: {response.status_code}")
            return False

    async def cleanup_test_data(self):
        """Limpiar datos de prueba"""
        print("\n🧹 Limpiando datos de prueba...")

        db = get_database()

        # Eliminar citas de prueba
        result = await db.citas.delete_many({"observaciones": {"$regex": "TEST:"}})
        print(f"✅ Eliminadas {result.deleted_count} citas de prueba")

        # Eliminar pacientes de prueba
        result = await db.pacientes.delete_many({"identificacion": {"$regex": "^TEST"}})
        print(f"✅ Eliminados {result.deleted_count} pacientes de prueba")

    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🧪 === PRUEBAS DE FILTROS DE CITAS ===")
        print(f"Timestamp: {datetime.now()}")

        try:
            # Configurar datos de prueba
            await self.setup_database()

            # Autenticarse
            if not self.authenticate():
                print("❌ No se pudo autenticar. Abortando pruebas.")
                return

            # Ejecutar pruebas
            tests = [
                ("Sin filtros", self.test_no_filters),
                ("Filtro por estado", self.test_filter_by_estado),
                ("Filtro por tipo de estudio", self.test_filter_by_tipo_estudio),
                ("Filtro por fecha", self.test_filter_by_fecha),
                ("Filtro por nombre", self.test_filter_by_paciente_nombre),
                ("Filtros combinados", self.test_combined_filters),
            ]

            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                try:
                    if test_func():
                        passed += 1
                    else:
                        print(f"❌ Falló: {test_name}")
                except Exception as e:
                    print(f"❌ Error en {test_name}: {e}")

            # Resumen
            print(f"\n📊 === RESUMEN ===")
            print(f"✅ Pruebas exitosas: {passed}/{total}")
            print(f"❌ Pruebas fallidas: {total - passed}/{total}")

            if passed == total:
                print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            else:
                print("⚠️  Algunas pruebas fallaron. Revisar la implementación.")

        except Exception as e:
            print(f"❌ Error general: {e}")
        finally:
            # Limpiar datos de prueba
            await self.cleanup_test_data()


async def main():
    """Función principal"""
    tester = CitasFilterTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
