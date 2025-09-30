#!/bin/bash

# Script para iniciar backend y frontend del sistema de imagenología
# Versión 1.3.0 - Incluye validaciones y creación automática de admin

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando servicios del sistema de imagenología v1.3.0${NC}"
echo ""

# Función para verificar y terminar procesos en un puerto
kill_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 Verificando puerto $port para $service_name...${NC}"
    
    # Buscar procesos usando el puerto
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}⚠️  Puerto $port en uso. Terminando procesos existentes...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null
        sleep 2
        echo -e "${GREEN}✅ Puerto $port liberado${NC}"
    else
        echo -e "${GREEN}✅ Puerto $port disponible${NC}"
    fi
}

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar señales para limpiar al salir
trap cleanup SIGINT SIGTERM

# Verificar que MongoDB está corriendo
echo -e "${YELLOW}🔍 Verificando MongoDB...${NC}"
if mongosh --eval "db.version()" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MongoDB está corriendo${NC}"
else
    echo -e "${RED}❌ MongoDB no está corriendo${NC}"
    echo -e "${YELLOW}Por favor inicia MongoDB primero:${NC}"
    echo "   sudo systemctl start mongod"
    exit 1
fi

# Verificar que existe el entorno virtual
if [ ! -d "backend/.venv" ]; then
    echo -e "${RED}❌ No se encontró el entorno virtual de Python${NC}"
    echo -e "${YELLOW}Creando entorno virtual...${NC}"
    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
fi

# Verificar que existen node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ No se encontraron dependencias de Node${NC}"
    echo -e "${YELLOW}Instalando dependencias...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
fi

# Verificar y liberar puertos
kill_port 8000 "Backend"
kill_port 4200 "Frontend"

# Crear directorio de uploads si no existe
if [ ! -d "backend/uploads/dicom" ]; then
    echo -e "${YELLOW}📁 Creando directorio de uploads...${NC}"
    mkdir -p backend/uploads/dicom
    echo -e "${GREEN}✅ Directorio creado${NC}"
fi

# Iniciar backend
echo ""
echo -e "${BLUE}📡 Iniciando backend (FastAPI)...${NC}"
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Esperar a que el backend inicie (reducido a 10 segundos max)
echo -e "${YELLOW}⏳ Esperando a que el backend inicie...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend iniciado correctamente${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Error al iniciar el backend${NC}"
        echo -e "${YELLOW}Ver logs en backend.log${NC}"
        tail -20 backend.log
        exit 1
    fi
    sleep 0.5  # Reducido de 1 segundo a 0.5 segundos
done

# Crear usuario administrador si no existe (en background para no retrasar)
echo ""
echo -e "${YELLOW}👤 Verificando usuario administrador...${NC}"
(
    sleep 2  # Esperar un poco para que el backend esté completamente listo
    ADMIN_CHECK=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@imagenologia.com","password":"admin123"}' 2>/dev/null)

    if echo "$ADMIN_CHECK" | grep -q "access_token"; then
        echo -e "${GREEN}✅ Usuario administrador ya existe${NC}"
    else
        echo -e "${YELLOW}📝 Creando usuario administrador...${NC}"
        ADMIN_CREATE=$(curl -s -X POST http://localhost:8000/api/auth/register \
          -H "Content-Type: application/json" \
          -d '{
            "email": "admin@imagenologia.com",
            "password": "admin123",
            "nombre": "Administrador",
            "apellidos": "Sistema",
            "role": "admin"
          }')
        
        if echo "$ADMIN_CREATE" | grep -q "id"; then
            echo -e "${GREEN}✅ Usuario administrador creado${NC}"
        else
            echo -e "${YELLOW}⚠️  Usuario admin ya existe o hubo un error${NC}"
        fi
    fi
) &

# Iniciar frontend
echo ""
echo -e "${BLUE}🎨 Iniciando frontend (Angular)...${NC}"
cd frontend
ng serve --port 4200 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Esperar a que el frontend compile completamente
echo -e "${YELLOW}⏳ Esperando a que el frontend compile...${NC}"
for i in {1..60}; do
    if grep -q "Application bundle generation complete" frontend.log 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend compilado correctamente${NC}"
        sleep 1  # Esperar un segundo adicional para asegurar que esté listo
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Frontend tardando más de lo esperado, pero continuando...${NC}"
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Servicios iniciados correctamente${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 URLs:${NC} 🌐 ${GREEN}http://localhost:4200${NC} | 🔌 ${GREEN}http://localhost:8000${NC} | 📚 ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${BLUE}👤 Admin:${NC} 📧 ${GREEN}admin@imagenologia.com${NC} | 🔑 ${GREEN}admin123${NC}"
echo -e "${BLUE}📝 Logs:${NC} ${YELLOW}tail -f backend.log${NC} | ${YELLOW}tail -f frontend.log${NC}"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener los servicios${NC}"
echo ""

# Esperar indefinidamente
wait
