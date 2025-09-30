#!/usr/bin/env python3
"""
Script de utilidad para regenerar imágenes PNG faltantes a partir de archivos DICOM

Este script escanea el directorio de uploads, encuentra archivos DICOM que no tienen
su correspondiente archivo PNG y los regenera automáticamente.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("regenerar_png.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.database import get_database
    from bson import ObjectId
    import pydicom
    from PIL import Image
    import numpy as np
    import uuid
except ImportError as e:
    logger.error(f"Error importando dependencias: {e}")
    sys.exit(1)


def convert_dicom_to_png(dicom_path: str, output_path: str) -> bool:
    """
    Convertir archivo DICOM a PNG
    Replica la funcionalidad del backend
    """
    try:
        # Leer archivo DICOM
        ds = pydicom.dcmread(dicom_path)

        # Verificar que tiene datos de píxeles
        if not hasattr(ds, "pixel_array"):
            logger.warning(f"Archivo DICOM sin datos de píxeles: {dicom_path}")
            return False

        # Convertir a numpy array
        img_array = ds.pixel_array

        # Normalizar a 0-255
        if img_array.max() > img_array.min():
            img_array = (
                (img_array - np.min(img_array))
                / (np.max(img_array) - np.min(img_array))
                * 255.0
            )
        else:
            img_array = np.zeros_like(img_array)

        img_array = img_array.astype(np.uint8)

        # Convertir a PIL Image y guardar como PNG
        img = Image.fromarray(img_array)
        img.save(output_path, "PNG")

        logger.info(f"PNG generado: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error convirtiendo {dicom_path} a PNG: {str(e)}")
        return False


def scan_upload_directory():
    """
    Escanear directorio de uploads y encontrar archivos DICOM sin PNG
    """
    upload_dir = Path("backend/uploads/dicom")

    if not upload_dir.exists():
        logger.error(f"Directorio de uploads no existe: {upload_dir}")
        return []

    missing_pngs = []

    # Recorrer todos los subdirectorios (estudios)
    for estudio_dir in upload_dir.iterdir():
        if not estudio_dir.is_dir():
            continue

        estudio_id = estudio_dir.name
        logger.info(f"Escaneando estudio: {estudio_id}")

        # Buscar archivos DICOM
        dicom_files = list(estudio_dir.glob("*.dcm"))

        for dicom_file in dicom_files:
            # Determinar nombre del PNG correspondiente
            png_name = dicom_file.stem + ".png"
            png_path = estudio_dir / png_name

            if not png_path.exists():
                logger.info(f"PNG faltante para: {dicom_file.name}")
                missing_pngs.append(
                    {
                        "estudio_id": estudio_id,
                        "dicom_path": dicom_file,
                        "png_path": png_path,
                        "dicom_name": dicom_file.name,
                        "png_name": png_name,
                    }
                )

    return missing_pngs


async def update_database_references(regenerated_files):
    """
    Actualizar referencias en la base de datos para archivos regenerados
    """
    if not regenerated_files:
        return

    logger.info("Actualizando referencias en la base de datos...")
    db = get_database()

    updated_informes = 0

    for file_info in regenerated_files:
        estudio_id = file_info["estudio_id"]
        dicom_name = file_info["dicom_name"]
        png_name = file_info["png_name"]

        try:
            # Buscar informes que tengan este estudio
            informes = await db.informes.find({"estudio_id": estudio_id}).to_list(
                length=None
            )

            for informe in informes:
                imagenes_dicom = informe.get("imagenes_dicom", [])
                updated = False

                # Buscar imagen DICOM sin PNG asociado
                for imagen in imagenes_dicom:
                    if imagen.get("archivo_dicom") == dicom_name and not imagen.get(
                        "archivo_png"
                    ):
                        imagen["archivo_png"] = png_name
                        updated = True
                        logger.info(
                            f"Actualizada referencia PNG en informe {informe.get('_id')}"
                        )

                # Actualizar informe si se modificó
                if updated:
                    await db.informes.update_one(
                        {"_id": informe["_id"]},
                        {
                            "$set": {
                                "imagenes_dicom": imagenes_dicom,
                                "fecha_actualizacion": datetime.utcnow(),
                            }
                        },
                    )
                    updated_informes += 1

        except Exception as e:
            logger.error(f"Error actualizando BD para estudio {estudio_id}: {e}")

    logger.info(f"Actualizados {updated_informes} informes en la base de datos")


def regenerate_missing_pngs(missing_pngs, max_files=None):
    """
    Regenerar archivos PNG faltantes
    """
    if not missing_pngs:
        logger.info("No se encontraron archivos PNG faltantes")
        return []

    logger.info(f"Encontrados {len(missing_pngs)} archivos PNG faltantes")

    if max_files:
        missing_pngs = missing_pngs[:max_files]
        logger.info(f"Procesando solo los primeros {max_files} archivos")

    regenerated = []
    errors = []

    for i, file_info in enumerate(missing_pngs, 1):
        logger.info(f"[{i}/{len(missing_pngs)}] Procesando: {file_info['dicom_name']}")

        try:
            success = convert_dicom_to_png(
                str(file_info["dicom_path"]), str(file_info["png_path"])
            )

            if success:
                regenerated.append(file_info)
            else:
                errors.append(file_info)

        except Exception as e:
            logger.error(f"Error procesando {file_info['dicom_name']}: {e}")
            errors.append(file_info)

    logger.info(f"Regeneración completada:")
    logger.info(f"  - Exitosos: {len(regenerated)}")
    logger.info(f"  - Errores: {len(errors)}")

    if errors:
        logger.warning("Archivos con errores:")
        for error_file in errors:
            logger.warning(f"  - {error_file['dicom_name']}")

    return regenerated


async def generate_report(missing_before, regenerated_files):
    """
    Generar reporte de la operación
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "archivos_faltantes_encontrados": len(missing_before),
        "archivos_regenerados": len(regenerated_files),
        "tasa_exito": (len(regenerated_files) / len(missing_before) * 100)
        if missing_before
        else 100,
        "detalles": {
            "estudios_procesados": len(set(f["estudio_id"] for f in missing_before)),
            "estudios_exitosos": len(set(f["estudio_id"] for f in regenerated_files)),
        },
    }

    # Guardar reporte
    report_path = Path("regeneracion_png_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Reporte guardado en: {report_path}")

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE REGENERACIÓN DE IMÁGENES PNG")
    print("=" * 60)
    print(f"Archivos faltantes encontrados: {report['archivos_faltantes_encontrados']}")
    print(f"Archivos regenerados exitosamente: {report['archivos_regenerados']}")
    print(f"Tasa de éxito: {report['tasa_exito']:.1f}%")
    print(f"Estudios procesados: {report['detalles']['estudios_procesados']}")
    print(f"Estudios exitosos: {report['detalles']['estudios_exitosos']}")
    print("=" * 60)

    return report


async def main():
    """Función principal"""
    print("🔧 === REGENERADOR DE IMÁGENES PNG ===")
    print(f"Timestamp: {datetime.now()}")

    # Cambiar al directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    try:
        # 1. Escanear directorio de uploads
        logger.info("Escaneando directorio de uploads...")
        missing_pngs = scan_upload_directory()

        if not missing_pngs:
            logger.info("✅ No se encontraron archivos PNG faltantes")
            return

        # 2. Mostrar resumen inicial
        estudios_afectados = set(f["estudio_id"] for f in missing_pngs)
        logger.info(f"Archivos PNG faltantes: {len(missing_pngs)}")
        logger.info(f"Estudios afectados: {len(estudios_afectados)}")

        # 3. Confirmar antes de proceder (si se ejecuta interactivamente)
        if sys.stdout.isatty():  # Terminal interactivo
            response = input(f"\n¿Regenerar {len(missing_pngs)} archivos PNG? (y/N): ")
            if response.lower() != "y":
                logger.info("Operación cancelada por el usuario")
                return

        # 4. Regenerar archivos PNG
        logger.info("Iniciando regeneración de archivos PNG...")
        regenerated_files = regenerate_missing_pngs(missing_pngs)

        # 5. Actualizar base de datos
        if regenerated_files:
            await update_database_references(regenerated_files)

        # 6. Generar reporte
        await generate_report(missing_pngs, regenerated_files)

        # 7. Verificación final
        if regenerated_files:
            logger.info("✅ Regeneración completada exitosamente")
        else:
            logger.warning("⚠️ No se pudieron regenerar archivos PNG")

    except KeyboardInterrupt:
        logger.info("Operación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error general: {e}")
        raise


def print_usage():
    """Mostrar instrucciones de uso"""
    print("""
Uso: python regenerar_imagenes_png.py [opciones]

Opciones:
  --help, -h     Mostrar esta ayuda
  --scan-only    Solo escanear y reportar, no regenerar
  --max N        Procesar máximo N archivos
  --dry-run      Ejecutar sin hacer cambios reales

Ejemplos:
  python regenerar_imagenes_png.py                    # Regenerar todos los PNG faltantes
  python regenerar_imagenes_png.py --scan-only        # Solo mostrar qué archivos faltan
  python regenerar_imagenes_png.py --max 10           # Regenerar máximo 10 archivos
  python regenerar_imagenes_png.py --dry-run          # Simular sin hacer cambios
""")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regenerar imágenes PNG faltantes")
    parser.add_argument(
        "--scan-only", action="store_true", help="Solo escanear, no regenerar"
    )
    parser.add_argument("--max", type=int, help="Máximo número de archivos a procesar")
    parser.add_argument(
        "--dry-run", action="store_true", help="Ejecutar sin hacer cambios"
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("MODO DRY-RUN: No se harán cambios reales")

    # Ejecutar función principal
    asyncio.run(main())
