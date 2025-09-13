"""
Punto de entrada principal de la aplicación
"""

from app import create_app
import uvicorn
import sys
import os

# Agregar el directorio raíz al path para importar server_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Crear la aplicación usando la función factory
app = create_app()

def main():
    """Función principal para ejecutar la aplicación"""
    
    try:
        from server_config import config
        
        # Validar configuración
        if not config.validate_config():
            print("❌ Error en la configuración. Verifique las variables de entorno.")
            sys.exit(1)
        
        # Obtener configuración de Uvicorn
        uvicorn_config = config.get_uvicorn_config()
        
        print(f"🚀 Iniciando servidor en {uvicorn_config['host']}:{uvicorn_config['port']}")
        print(f"🌍 Entorno: {config.environment}")
        print(f"🔧 Debug: {config.debug}")
        print(f"📝 Log level: {config.log_level}")
        
        # Ejecutar el servidor
        uvicorn.run(
            "app.main:app",
            **uvicorn_config
        )
    except ImportError:
        # Fallback si server_config no está disponible
        print("🚀 Iniciando servidor en modo simple...")
        uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
