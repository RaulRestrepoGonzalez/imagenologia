"""
Configuración de logging para la aplicación
"""

import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configurar el sistema de logging"""
    
    # Crear directorio de logs si no existe
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato del log
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('motor').setLevel(logging.WARNING)
    
    # Log de inicio
    logging.info("Sistema de logging configurado correctamente")
    logging.info(f"Nivel de log: {log_level}")
    if log_file:
        logging.info(f"Archivo de log: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Obtener un logger específico"""
    return logging.getLogger(name)



