#!/usr/bin/env python3
"""
Script para ejecutar tests del backend
"""

import subprocess
import sys
import os

def run_tests():
    """Ejecutar tests con pytest"""
    print("🧪 Ejecutando tests del backend...")
    print("=" * 50)
    
    # Verificar que pytest esté instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "httpx"])
    
    # Ejecutar tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    # Agregar argumentos si se proporcionan
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print(f"Comando: {' '.join(cmd)}")
    print()
    
    # Ejecutar tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Todos los tests pasaron exitosamente!")
    else:
        print("\n❌ Algunos tests fallaron.")
        sys.exit(1)

def run_specific_tests():
    """Ejecutar tests específicos"""
    print("🎯 Ejecutando tests específicos...")
    print("=" * 50)
    
    # Tests de pacientes
    print("\n📋 Ejecutando tests de pacientes...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_pacientes.py", "-v"])
    
    # Tests de citas
    print("\n📅 Ejecutando tests de citas...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_citas.py", "-v"])
    
    # Tests de informes
    print("\n📊 Ejecutando tests de informes...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_informes.py", "-v"])

def run_tests_with_coverage():
    """Ejecutar tests con cobertura"""
    print("📊 Ejecutando tests con cobertura...")
    print("=" * 50)
    
    # Instalar coverage si no está instalado
    try:
        import coverage
    except ImportError:
        print("Instalando coverage...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-cov"])
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "specific":
            run_specific_tests()
        elif sys.argv[1] == "coverage":
            run_tests_with_coverage()
        else:
            print("Uso: python run_tests.py [specific|coverage]")
            print("  specific: Ejecutar tests específicos por módulo")
            print("  coverage: Ejecutar tests con cobertura")
            print("  (sin argumentos): Ejecutar todos los tests")
    else:
        run_tests()



