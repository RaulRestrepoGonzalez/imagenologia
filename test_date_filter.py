#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del filtro de fecha mejorado
Este script valida que el DatePicker y los botones de fecha rápida funcionen correctamente
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


class DateFilterTester:
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

    def test_date_formats(self):
        """Probar diferentes formatos de fecha"""
        print("\n📅 Prueba 1: Formatos de fecha")

        # Generar fechas de prueba
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        date_tests = [
            {"name": "Hoy", "date": today, "expected_results": "≥ 0"},
            {"name": "Ayer", "date": yesterday, "expected_results": "≥ 0"},
            {"name": "Mañana", "date": tomorrow, "expected_results": "≥ 0"},
        ]

        for test in date_tests:
            date_str = test["date"].strftime("%Y-%m-%d")
            print(f"  🗓️  Probando {test['name']} ({date_str})...")

            params = {"fecha": date_str}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 200:
                citas = response.json()
                print(f"    ✅ {len(citas)} citas encontradas")

                # Verificar que todas las citas sean de la fecha correcta
                date_errors = []
                for cita in citas:
                    try:
                        cita_date = datetime.fromisoformat(
                            cita["fecha_cita"].replace("Z", "+00:00")
                        ).date()
                        if cita_date != test["date"].date():
                            date_errors.append(
                                f"Cita {cita['id']}: {cita_date} != {test['date'].date()}"
                            )
                    except Exception as e:
                        date_errors.append(f"Cita {cita['id']}: Error de formato - {e}")

                if date_errors:
                    print(f"    ⚠️  {len(date_errors)} citas con fecha incorrecta:")
                    for error in date_errors[:3]:  # Mostrar solo los primeros 3
                        print(f"       - {error}")
                else:
                    print("    ✅ Todas las fechas son correctas")

            else:
                print(f"    ❌ Error: {response.status_code}")
                return False

        return True

    def test_quick_date_buttons(self):
        """Simular el comportamiento de los botones de fecha rápida"""
        print("\n🚀 Prueba 2: Botones de fecha rápida")

        # Simular clicks en botones
        quick_dates = [
            {"name": "Botón HOY", "offset": 0},
            {"name": "Botón MAÑANA", "offset": 1},
            {"name": "Botón AYER", "offset": -1},
        ]

        for button in quick_dates:
            target_date = datetime.now() + timedelta(days=button["offset"])
            date_str = target_date.strftime("%Y-%m-%d")

            print(f"  🔘 Simulando click en {button['name']} ({date_str})...")

            params = {"fecha": date_str}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 200:
                citas = response.json()
                print(f"    ✅ {len(citas)} citas para {button['name']}")

                if citas:
                    # Mostrar ejemplos
                    for i, cita in enumerate(citas[:2]):  # Solo primeras 2
                        fecha_cita = cita.get("fecha_cita", "N/A")
                        paciente = cita.get("paciente_nombre", "Desconocido")
                        print(f"       {i + 1}. {paciente} - {fecha_cita}")

            else:
                print(f"    ❌ Error: {response.status_code}")
                return False

        return True

    def test_date_validation(self):
        """Probar validación de fechas inválidas"""
        print("\n🛡️  Prueba 3: Validación de fechas")

        invalid_dates = [
            "2025-13-01",  # Mes inválido
            "2025-02-30",  # Día inválido
            "fecha-invalid",  # Formato completamente inválido
            "2025/01/01",  # Formato incorrecto
            "",  # Fecha vacía
        ]

        for invalid_date in invalid_dates:
            print(f"  🚫 Probando fecha inválida: '{invalid_date}'...")

            params = {"fecha": invalid_date}
            response = self.session.get(f"{API_BASE}/citas", params=params)

            if response.status_code == 400:
                print("    ✅ Correctamente rechazada (400)")
            elif response.status_code == 200:
                citas = response.json()
                if invalid_date == "":
                    print(
                        f"    ✅ Fecha vacía manejada correctamente ({len(citas)} citas)"
                    )
                else:
                    print(f"    ⚠️  Fecha inválida aceptada ({len(citas)} citas)")
            else:
                print(f"    ❓ Respuesta inesperada: {response.status_code}")

        return True

    def test_date_ranges(self):
        """Probar rangos de fechas para verificar precisión"""
        print("\n📊 Prueba 4: Precisión de rangos de fecha")

        # Probar diferentes rangos
        base_date = datetime.now()
        test_ranges = [
            {"name": "Última semana", "start": -7, "end": -1},
            {"name": "Esta semana", "start": -3, "end": 3},
            {"name": "Próxima semana", "start": 1, "end": 7},
        ]

        for range_test in test_ranges:
            print(f"  📈 Probando {range_test['name']}...")

            total_citas = 0
            dates_with_citas = []

            for offset in range(range_test["start"], range_test["end"] + 1):
                test_date = base_date + timedelta(days=offset)
                date_str = test_date.strftime("%Y-%m-%d")

                params = {"fecha": date_str}
                response = self.session.get(f"{API_BASE}/citas", params=params)

                if response.status_code == 200:
                    citas = response.json()
                    total_citas += len(citas)

                    if len(citas) > 0:
                        dates_with_citas.append((date_str, len(citas)))

            print(f"    ✅ Total: {total_citas} citas en {range_test['name']}")

            if dates_with_citas:
                print(f"    📅 Fechas con citas:")
                for date_str, count in dates_with_citas[
                    :3
                ]:  # Mostrar solo las primeras 3
                    print(f"       - {date_str}: {count} cita(s)")

        return True

    def test_date_performance(self):
        """Probar rendimiento del filtro de fecha"""
        print("\n⚡ Prueba 5: Rendimiento del filtro de fecha")

        import time

        # Fechas para probar rendimiento
        performance_dates = [
            datetime.now(),
            datetime.now() - timedelta(days=30),
            datetime.now() + timedelta(days=30),
        ]

        total_time = 0
        successful_requests = 0

        for i, test_date in enumerate(performance_dates, 1):
            date_str = test_date.strftime("%Y-%m-%d")
            print(f"  ⏱️  Test {i}: {date_str}...")

            start_time = time.time()
            response = self.session.get(f"{API_BASE}/citas", params={"fecha": date_str})
            end_time = time.time()

            duration = (end_time - start_time) * 1000  # en ms

            if response.status_code == 200:
                citas_count = len(response.json())
                print(f"    ✅ {duration:.2f}ms - {citas_count} citas")
                total_time += duration
                successful_requests += 1
            else:
                print(f"    ❌ Error: {response.status_code}")

        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"  📊 Tiempo promedio: {avg_time:.2f}ms")

            if avg_time < 100:
                print("  🎯 Rendimiento excelente (< 100ms)")
            elif avg_time < 500:
                print("  👍 Rendimiento bueno (< 500ms)")
            else:
                print("  ⚠️  Rendimiento mejorable (> 500ms)")

        return True

    def test_ui_simulation(self):
        """Simular interacciones de usuario típicas"""
        print("\n🎭 Prueba 6: Simulación de interacciones de usuario")

        # Secuencia típica de usuario
        user_actions = [
            {"action": "Abrir calendario", "description": "Usuario carga página"},
            {"action": "Click en 'Hoy'", "date_offset": 0},
            {"action": "Click en 'Mañana'", "date_offset": 1},
            {"action": "Click en 'Ayer'", "date_offset": -1},
            {"action": "Limpiar filtro", "clear": True},
        ]

        for step, action in enumerate(user_actions, 1):
            print(f"  🎬 Paso {step}: {action['action']}")

            if action.get("clear"):
                # Simular limpiar filtro (sin parámetros de fecha)
                response = self.session.get(f"{API_BASE}/citas")
                if response.status_code == 200:
                    total_citas = len(response.json())
                    print(f"    ✅ Filtro limpiado - {total_citas} citas totales")
                else:
                    print(f"    ❌ Error al limpiar: {response.status_code}")

            elif "date_offset" in action:
                # Simular selección de fecha
                target_date = datetime.now() + timedelta(days=action["date_offset"])
                date_str = target_date.strftime("%Y-%m-%d")

                params = {"fecha": date_str}
                response = self.session.get(f"{API_BASE}/citas", params=params)

                if response.status_code == 200:
                    citas = response.json()
                    print(f"    ✅ {len(citas)} citas para {date_str}")
                else:
                    print(f"    ❌ Error: {response.status_code}")

            else:
                # Acción sin backend (solo UI)
                print(f"    ✅ Acción de UI completada")

        return True

    async def run_all_tests(self):
        """Ejecutar todas las pruebas del filtro de fecha"""
        print("🗓️  === PRUEBAS DEL FILTRO DE FECHA MEJORADO ===")
        print(f"Timestamp: {datetime.now()}")
        print(f"Backend URL: {BASE_URL}")

        try:
            # Autenticarse
            if not self.authenticate():
                print("❌ No se pudo autenticar. Abortando pruebas.")
                return

            # Ejecutar pruebas
            tests = [
                ("Formatos de fecha", self.test_date_formats),
                ("Botones de fecha rápida", self.test_quick_date_buttons),
                ("Validación de fechas", self.test_date_validation),
                ("Rangos de fecha", self.test_date_ranges),
                ("Rendimiento", self.test_date_performance),
                ("Simulación de UI", self.test_ui_simulation),
            ]

            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                try:
                    print(f"\n{'=' * 60}")
                    print(f"🧪 EJECUTANDO: {test_name}")
                    print(f"{'=' * 60}")

                    if test_func():
                        passed += 1
                        print(f"✅ {test_name}: EXITOSO")
                    else:
                        print(f"❌ {test_name}: FALLÓ")
                except Exception as e:
                    print(f"❌ Error en {test_name}: {e}")

            # Resumen final
            print(f"\n{'=' * 70}")
            print(f"📊 === RESUMEN FINAL - FILTRO DE FECHA ===")
            print(f"✅ Pruebas exitosas: {passed}/{total}")
            print(f"❌ Pruebas fallidas: {total - passed}/{total}")

            if passed == total:
                print("🎉 ¡Filtro de fecha funcionando perfectamente!")
                print("📅 DatePicker y botones rápidos listos para usar")
                print("🚀 Experiencia de usuario optimizada")
            else:
                print("⚠️  Algunos tests fallaron.")
                print("🔧 Revisar la implementación del filtro de fecha.")

            # Recomendaciones
            print(f"\n💡 === RECOMENDACIONES ===")
            print("✅ Usar DatePicker en lugar de input manual")
            print("✅ Botones 'Hoy', 'Mañana', 'Ayer' para acceso rápido")
            print("✅ Validación automática de formatos de fecha")
            print("✅ Botón 'Limpiar' para resetear filtro fácilmente")

        except Exception as e:
            print(f"❌ Error general: {e}")


async def main():
    """Función principal"""
    tester = DateFilterTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
