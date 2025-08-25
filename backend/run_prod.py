#!/usr/bin/env python3
"""
Script para ejecutar la aplicación en modo producción
"""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    print("🚀 Iniciando aplicación en modo producción...")
    
    # Configuración para producción
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
        log_level="info",
        access_log=True,
        workers=int(os.getenv("WORKERS", "4"))
    )



