#!/bin/bash

# Script para iniciar backend y frontend del sistema de imagenología

echo "🚀 Iniciando servicios del sistema de imagenología..."

# Función para verificar y terminar procesos en un puerto
kill_port() {
    local port=$1
    local service_name=$2
    
    echo "🔍 Verificando puerto $port para $service_name..."
    
    # Buscar procesos usando el puerto
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo "⚠️  Puerto $port en uso. Terminando procesos existentes..."
        echo "$pids" | xargs kill -9 2>/dev/null
        sleep 2
        echo "✅ Puerto $port liberado"
    else
        echo "✅ Puerto $port disponible"
    fi
}

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar señales para limpiar al salir
trap cleanup SIGINT SIGTERM

# Verificar y liberar puertos
kill_port 8000 "Backend"
kill_port 4200 "Frontend"

# Iniciar backend
echo "📡 Iniciando backend (FastAPI)..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Esperar un momento para que el backend inicie
sleep 3

# Verificar que el backend esté corriendo
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend iniciado correctamente"
else
    echo "❌ Error al iniciar el backend"
    exit 1
fi

# Iniciar frontend
echo "🎨 Iniciando frontend (Angular)..."
cd frontend
ng serve --port 4200 &
FRONTEND_PID=$!
cd ..

echo "✅ Servicios iniciados:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:4200"
echo "   Docs API: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios"

# Esperar indefinidamente
wait
