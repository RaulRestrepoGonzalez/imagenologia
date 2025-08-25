# Tests del Backend

Este directorio contiene todos los tests para el backend del sistema médico.

## 🏗️ Estructura de Tests

```
tests/
├── __init__.py              # Paquete de tests
├── conftest.py              # Configuración y fixtures comunes
├── test_config.py           # Configuración específica para tests
├── test_pacientes.py        # Tests para el módulo de pacientes
├── test_citas.py            # Tests para el módulo de citas
├── test_informes.py         # Tests para el módulo de informes
└── README.md                # Este archivo
```

## 🚀 Ejecutar Tests

### Opción 1: Script personalizado (Recomendado)
```bash
# Ejecutar todos los tests
python run_tests.py

# Ejecutar tests específicos por módulo
python run_tests.py specific

# Ejecutar tests con cobertura
python run_tests.py coverage
```

### Opción 2: Con pytest directamente
```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/test_pacientes.py
pytest tests/test_citas.py
pytest tests/test_informes.py

# Ejecutar tests con más detalle
pytest -v

# Ejecutar tests con cobertura
pytest --cov=app --cov-report=term-missing
```

### Opción 3: Tests específicos
```bash
# Solo tests de pacientes
pytest tests/test_pacientes.py -v

# Solo tests de citas
pytest tests/test_citas.py -v

# Solo tests de informes
pytest tests/test_informes.py -v

# Tests con marcadores específicos
pytest -m "not slow"
pytest -m "unit"
```

## 📋 Requisitos para Tests

### Dependencias
```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

### Base de Datos
- MongoDB ejecutándose en `localhost:27017`
- Base de datos de test: `ips_imagenologia_test`

### Variables de Entorno
```bash
# Crear archivo .env.test en la carpeta tests
TEST_MONGO_URI=mongodb://localhost:27017
TEST_DATABASE_NAME=ips_imagenologia_test
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🧪 Tipos de Tests

### Tests de Pacientes (`test_pacientes.py`)
- ✅ Crear paciente exitosamente
- ✅ Validar duplicados (identificación, email)
- ✅ Obtener lista de pacientes con paginación
- ✅ Obtener paciente por ID
- ✅ Actualizar paciente
- ✅ Eliminar paciente (soft delete)
- ✅ Obtener estudios de un paciente
- ✅ Validación de datos

### Tests de Citas (`test_citas.py`)
- ✅ Crear cita exitosamente
- ✅ Validar conflictos de horario (sala, técnico)
- ✅ Obtener lista de citas con filtros
- ✅ Obtener cita por ID
- ✅ Actualizar cita
- ✅ Cancelar cita
- ✅ Actualizar asistencia
- ✅ Validación de datos

### Tests de Informes (`test_informes.py`)
- ✅ Obtener estadísticas exitosamente
- ✅ Validar fechas inválidas
- ✅ Estadísticas por estado de estudio
- ✅ Estadísticas por tipo de estudio
- ✅ Estadísticas de citas por estado
- ✅ Tasa de asistencia
- ✅ Rango de fechas vacío
- ✅ Ordenamiento de estadísticas
- ✅ Agregación correcta de datos

## 🔧 Configuración de Tests

### Fixtures Comunes
- `test_database`: Base de datos de test limpia
- `test_client`: Cliente HTTP para tests
- `sample_paciente_data`: Datos de ejemplo para pacientes
- `sample_estudio_data`: Datos de ejemplo para estudios
- `sample_cita_data`: Datos de ejemplo para citas
- `sample_informe_data`: Datos de ejemplo para informes
- `paciente_creado`: Paciente creado para tests
- `estudio_creado`: Estudio creado para tests
- `cita_creada`: Cita creada para tests

### Configuración de Base de Datos
- Cada test session crea una base de datos limpia
- Los tests se ejecutan en paralelo de forma segura
- Limpieza automática después de cada test

## 📊 Cobertura de Tests

Para generar reportes de cobertura:

```bash
# Instalar pytest-cov
pip install pytest-cov

# Ejecutar tests con cobertura
pytest --cov=app --cov-report=term-missing --cov-report=html

# Ver reporte HTML
open htmlcov/index.html
```

## 🚨 Troubleshooting

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio backend
cd backend

# Ejecutar tests desde ahí
python -m pytest tests/
```

### Error: "Connection refused" (MongoDB)
```bash
# Verificar que MongoDB esté ejecutándose
mongod --version
systemctl status mongod  # En Linux

# Iniciar MongoDB si no está ejecutándose
mongod
```

### Error: "ModuleNotFoundError: No module named 'pytest'"
```bash
# Instalar dependencias de testing
pip install -r requirements.txt

# O instalar manualmente
pip install pytest pytest-asyncio httpx
```

### Tests muy lentos
```bash
# Ejecutar tests en paralelo
pytest -n auto

# O ejecutar solo tests específicos
pytest tests/test_pacientes.py -v
```

## 📝 Agregar Nuevos Tests

### 1. Crear archivo de test
```python
# tests/test_nuevo_modulo.py
import pytest
from httpx import AsyncClient

class TestNuevoModulo:
    async def test_nueva_funcionalidad(self, test_client: AsyncClient):
        # Tu test aquí
        pass
```

### 2. Agregar fixtures si es necesario
```python
# En conftest.py
@pytest.fixture
def sample_nuevo_data():
    return {
        "campo1": "valor1",
        "campo2": "valor2"
    }
```

### 3. Ejecutar tests
```bash
pytest tests/test_nuevo_modulo.py -v
```

## 🎯 Mejores Prácticas

1. **Nombres descriptivos**: Usar nombres claros para tests y funciones
2. **Un test por funcionalidad**: Cada test debe verificar una cosa específica
3. **Fixtures reutilizables**: Usar fixtures para datos comunes
4. **Validación completa**: Verificar tanto casos exitosos como de error
5. **Limpieza de datos**: Usar base de datos de test separada
6. **Tests independientes**: Cada test debe poder ejecutarse solo

## 📞 Soporte

Si tienes problemas con los tests:

1. Verificar que MongoDB esté ejecutándose
2. Verificar que todas las dependencias estén instaladas
3. Revisar los logs de error
4. Ejecutar tests individuales para identificar el problema
5. Verificar la configuración de variables de entorno



