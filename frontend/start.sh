#!/bin/bash

# ========================================
# SISTEMA CLÍNICO - SCRIPT DE INICIO RÁPIDO
# ========================================

echo "🏥 Iniciando Sistema Clínico..."
echo "=================================="

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js no está instalado"
    echo "Por favor, instala Node.js desde: https://nodejs.org/"
    exit 1
fi

# Verificar versión de Node.js
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js versión 18 o superior es requerida"
    echo "Versión actual: $(node -v)"
    echo "Por favor, actualiza Node.js desde: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node -v) detectado"

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm no está instalado"
    exit 1
fi

echo "✅ npm $(npm -v) detectado"

# Verificar si Angular CLI está instalado
if ! command -v ng &> /dev/null; then
    echo "📦 Instalando Angular CLI..."
    npm install -g @angular/cli
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo instalar Angular CLI"
        exit 1
    fi
fi

echo "✅ Angular CLI $(ng version | grep 'Angular CLI' | cut -d' ' -f3) detectado"

# Verificar si las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias del proyecto..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudieron instalar las dependencias"
        exit 1
    fi
    echo "✅ Dependencias instaladas correctamente"
else
    echo "✅ Dependencias ya están instaladas"
fi

# Verificar si hay actualizaciones de dependencias
echo "🔍 Verificando actualizaciones de dependencias..."
npm outdated --depth=0

# Iniciar el servidor de desarrollo
echo "🚀 Iniciando servidor de desarrollo..."
echo "La aplicación estará disponible en: http://localhost:4200"
echo "Presiona Ctrl+C para detener el servidor"
echo ""

ng serve --open

