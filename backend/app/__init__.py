"""
Aplicación principal del proyecto backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys

# Agregar el directorio raíz al path para importar logging_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import setup_logging

# Cargar variables de entorno
load_dotenv()

def create_app(config_name=None):
    """Factory function para crear la aplicación FastAPI"""
    
    # Configurar logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    setup_logging(log_level, log_file)
    
    app = FastAPI(
        title="Sistema de Gestión de Imágenes Diagnósticas",
        description="Sistema integral para la automatización del servicio de imágenes diagnósticas",
        version="1.0.0"
    )
    
    # Configuración básica
    app.debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Habilitar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registrar rutas
    from app.routes import pacientes, estudios, citas, informes, notificaciones
    
    app.include_router(pacientes.router, prefix="/api", tags=["Pacientes"])
    app.include_router(estudios.router, prefix="/api", tags=["Estudios"])
    app.include_router(citas.router, prefix="/api", tags=["Citas"])
    app.include_router(informes.router, prefix="/api", tags=["Informes"])
    app.include_router(notificaciones.router, prefix="/api", tags=["Notificaciones"])
    
    # Eventos de startup y shutdown
    @app.on_event("startup")
    async def startup_event():
        """Evento que se ejecuta al iniciar la aplicación"""
        try:
            from app.database import init_database, test_connection
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Probar conexión a la base de datos
            if await test_connection():
                # Inicializar base de datos
                await init_database()
                logger.info("Aplicación iniciada correctamente")
            else:
                logger.error("No se pudo conectar a la base de datos")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en startup: {str(e)}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Evento que se ejecuta al cerrar la aplicación"""
        try:
            from app.database import close_database
            import logging
            
            logger = logging.getLogger(__name__)
            await close_database()
            logger.info("Aplicación cerrada correctamente")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en shutdown: {str(e)}")
    
    # Ruta de prueba
    @app.get("/")
    async def home():
        return {'message': '¡Bienvenido a la API del proyecto médico!', 'status': 'success'}
    
    @app.get("/health")
    async def health_check():
        from datetime import datetime
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    
    return app
