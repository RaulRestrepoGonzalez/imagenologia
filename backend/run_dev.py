#!/usr/bin/env python3
"""
Script para ejecutar la aplicación en modo desarrollo
"""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    print("🚀 Iniciando aplicación en modo desarrollo...")
    
    # Configuración para desarrollo
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True,
        use_colors=True
    )



