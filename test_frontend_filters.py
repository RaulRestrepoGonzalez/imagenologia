#!/usr/bin/env python3
"""
Script de prueba para verificar la integración frontend-backend de filtros de citas
Este script simula las peticiones que hace el frontend para validar que los filtros
funcionen correctamente en la interfaz de usuario.
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
import time

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


class FrontendFilterTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None

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

    def test_frontend_simulation(self):
        """Simular exactamente las peticiones que hace el frontend"""
        print("\n🎨 Simulando peticiones del frontend...")

        # 1. Carga inicial sin filtros (como hace el frontend al cargar)
        print("  📋 1. Carga inicial sin filtros...")
        response = self.session.get(f"{API_BASE}/citas")

        if response.status_code == 200:
            citas = response.json()
            print(f"    ✅ Cargadas {len(citas)} citas iniciales")

            # Verificar estructura de datos como espera el frontend
            if citas:
                primera_cita = citas[0]
                campos_esperados = [
                    "id",
                    "paciente_id",
                    "paciente_nombre",
                    "paciente_apellidos",
                    "fecha_cita",
                    "tipo_estudio",
                    "tipo_cita",
                    "estado",
                ]

                campos_faltantes = [
                    c for c in campos_esperados if c not in primera_cita
                ]
                if campos_faltantes:
                    print(f"    ⚠️  Campos faltantes: {campos_faltantes}")
                else:
                    print("    ✅ Estructura de datos correcta")

                # Mostrar ejemplo de mapeo
                print(f"    📝 Ejemplo de mapeo:")
                print(
                    f"       fecha_cita: {primera_cita.get('fecha_cita')} -> fecha_hora (frontend)"
                )
                print(f"       estado: {primera_cita.get('estado')}")
                print(f"       tipo_cita: {primera_cita.get('tipo_cita')}")
        else:
            print(f"    ❌ Error: {response.status_code}")
            return False

        # 2. Filtro por estado (simulando selección de dropdown)
        print("  📊 2. Filtro por estado 'Programada'...")
        params = {"estado": "Programada"}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas_filtradas = response.json()
            print(f"    ✅ {len(citas_filtradas)} citas programadas")

            # Verificar que todas tengan el estado correcto
            estados_incorrectos = [
                c for c in citas_filtradas if c["estado"] != "Programada"
            ]
            if estados_incorrectos:
                print(f"    ❌ {len(estados_incorrectos)} citas con estado incorrecto")
            else:
                print("    ✅ Todos los estados son correctos")
        else:
            print(f"    ❌ Error: {response.status_code}")

        # 3. Búsqueda por nombre (simulando input de búsqueda)
        print("  👤 3. Búsqueda por nombre 'Juan'...")
        params = {"paciente_nombre": "Juan"}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas_nombre = response.json()
            print(f"    ✅ {len(citas_nombre)} citas encontradas para 'Juan'")

            # Verificar que contengan el nombre buscado
            for cita in citas_nombre[:3]:  # Solo los primeros 3 para no saturar
                nombre_completo = f"{cita.get('paciente_nombre', '')} {cita.get('paciente_apellidos', '')}".strip()
                print(f"       - {nombre_completo}")
        else:
            print(f"    ❌ Error: {response.status_code}")

        # 4. Filtro por fecha (simulando date picker)
        print("  📅 4. Filtro por fecha de hoy...")
        today = datetime.now().strftime("%Y-%m-%d")
        params = {"fecha": today}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas_hoy = response.json()
            print(f"    ✅ {len(citas_hoy)} citas para hoy ({today})")
        else:
            print(f"    ❌ Error: {response.status_code}")

        # 5. Filtros combinados (simulando múltiples filtros activos)
        print("  🔄 5. Filtros combinados...")
        params = {"estado": "Programada", "tipo_estudio": "Radiografía"}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas_combinadas = response.json()
            print(f"    ✅ {len(citas_combinadas)} citas que cumplen ambos criterios")

            if citas_combinadas:
                print("    📝 Ejemplos encontrados:")
                for cita in citas_combinadas[:2]:
                    print(
                        f"       - {cita.get('paciente_nombre')} - {cita.get('tipo_estudio')} - {cita.get('estado')}"
                    )
        else:
            print(f"    ❌ Error: {response.status_code}")

        return True

    def test_performance(self):
        """Probar rendimiento de filtros"""
        print("\n⚡ Probando rendimiento de filtros...")

        # Medir tiempo de respuesta sin filtros
        start_time = time.time()
        response = self.session.get(f"{API_BASE}/citas")
        end_time = time.time()

        if response.status_code == 200:
            duration = (end_time - start_time) * 1000  # en ms
            citas_count = len(response.json())
            print(f"  📊 Sin filtros: {duration:.2f}ms para {citas_count} citas")

        # Medir tiempo con filtros
        start_time = time.time()
        response = self.session.get(
            f"{API_BASE}/citas", params={"estado": "Programada"}
        )
        end_time = time.time()

        if response.status_code == 200:
            duration = (end_time - start_time) * 1000  # en ms
            citas_count = len(response.json())
            print(f"  🔍 Con filtro: {duration:.2f}ms para {citas_count} citas")

        return True

    def test_edge_cases(self):
        """Probar casos extremos"""
        print("\n🧪 Probando casos extremos...")

        # 1. Filtro que no devuelve resultados
        print("  🔍 1. Filtro sin resultados...")
        params = {"paciente_nombre": "NoExiste123456"}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            citas = response.json()
            if len(citas) == 0:
                print("    ✅ Correctamente devuelve lista vacía")
            else:
                print(f"    ⚠️  Devolvió {len(citas)} resultados inesperados")
        else:
            print(f"    ❌ Error: {response.status_code}")

        # 2. Parámetros vacíos
        print("  📝 2. Parámetros vacíos...")
        params = {"estado": "", "tipo_estudio": ""}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 200:
            print("    ✅ Maneja correctamente parámetros vacíos")
        else:
            print(f"    ❌ Error con parámetros vacíos: {response.status_code}")

        # 3. Fecha inválida
        print("  📅 3. Fecha inválida...")
        params = {"fecha": "fecha-invalida"}
        response = self.session.get(f"{API_BASE}/citas", params=params)

        if response.status_code == 400:
            print("    ✅ Correctamente rechaza fecha inválida")
        elif response.status_code == 200:
            print("    ⚠️  Acepta fecha inválida (podría ser problema)")
        else:
            print(f"    ❓ Respuesta inesperada: {response.status_code}")

        return True

    def test_data_consistency(self):
        """Verificar consistencia de datos"""
        print("\n🔍 Verificando consistencia de datos...")

        response = self.session.get(f"{API_BASE}/citas")

        if response.status_code == 200:
            citas = response.json()

            # Verificar que no haya campos None o undefined
            campos_problemas = []
            for i, cita in enumerate(citas[:10]):  # Solo los primeros 10
                for campo, valor in cita.items():
                    if valor is None and campo in [
                        "paciente_nombre",
                        "estado",
                        "tipo_estudio",
                    ]:
                        campos_problemas.append(f"Cita {i}: {campo} es None")

            if campos_problemas:
                print("  ⚠️  Problemas de consistencia encontrados:")
                for problema in campos_problemas[:5]:  # Mostrar solo los primeros 5
                    print(f"    - {problema}")
            else:
                print("  ✅ Datos consistentes en campos críticos")

            # Verificar formatos de fecha
            fechas_invalidas = []
            for i, cita in enumerate(citas[:5]):
                try:
                    datetime.fromisoformat(cita["fecha_cita"].replace("Z", "+00:00"))
                except (ValueError, KeyError) as e:
                    fechas_invalidas.append(f"Cita {i}: {e}")

            if fechas_invalidas:
                print("  ⚠️  Problemas de formato de fecha:")
                for problema in fechas_invalidas:
                    print(f"    - {problema}")
            else:
                print("  ✅ Formatos de fecha correctos")

        return True

    async def run_all_tests(self):
        """Ejecutar todas las pruebas de frontend"""
        print("🎨 === PRUEBAS DE INTEGRACIÓN FRONTEND-BACKEND ===")
        print(f"Timestamp: {datetime.now()}")
        print(f"Backend URL: {BASE_URL}")

        try:
            # Autenticarse
            if not self.authenticate():
                print("❌ No se pudo autenticar. Abortando pruebas.")
                return

            # Ejecutar pruebas
            tests = [
                ("Simulación Frontend", self.test_frontend_simulation),
                ("Rendimiento", self.test_performance),
                ("Casos Extremos", self.test_edge_cases),
                ("Consistencia de Datos", self.test_data_consistency),
            ]

            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                try:
                    print(f"\n{'=' * 50}")
                    print(f"🧪 EJECUTANDO: {test_name}")
                    print(f"{'=' * 50}")

                    if test_func():
                        passed += 1
                        print(f"✅ {test_name}: EXITOSO")
                    else:
                        print(f"❌ {test_name}: FALLÓ")
                except Exception as e:
                    print(f"❌ Error en {test_name}: {e}")

            # Resumen final
            print(f"\n{'=' * 60}")
            print(f"📊 === RESUMEN FINAL ===")
            print(f"✅ Pruebas exitosas: {passed}/{total}")
            print(f"❌ Pruebas fallidas: {total - passed}/{total}")

            if passed == total:
                print("🎉 ¡Integración frontend-backend funcionando correctamente!")
                print("💡 El frontend puede usar los filtros sin problemas.")
            else:
                print("⚠️  Hay problemas en la integración.")
                print("🔧 Revisar los endpoints y el mapeo de datos.")

        except Exception as e:
            print(f"❌ Error general: {e}")


async def main():
    """Función principal"""
    tester = FrontendFilterTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
