#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo de impresión de informes con imágenes DICOM
Este script ayuda a diagnosticar problemas con la carga y visualización de imágenes
en la funcionalidad de impresión de informes.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio backend al path para importar módulos
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.database import get_database
    from bson import ObjectId
    import pydicom
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    print(
        "Asegúrate de estar en el directorio correcto y tener las dependencias instaladas"
    )
    sys.exit(1)


async def test_database_connection():
    """Probar conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    try:
        db = get_database()
        # Probar una consulta simple
        count = await db.informes.count_documents({})
        print(f"✅ Conexión exitosa. Total de informes en BD: {count}")
        return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False


async def find_informes_with_images():
    """Buscar informes que tengan imágenes DICOM"""
    print("\n🔍 Buscando informes con imágenes DICOM...")
    db = get_database()

    try:
        # Buscar informes que tengan el campo imagenes_dicom con al menos una imagen
        informes = await db.informes.find(
            {"imagenes_dicom": {"$exists": True, "$not": {"$size": 0}}}
        ).to_list(length=10)

        print(f"✅ Encontrados {len(informes)} informes con imágenes")

        for i, informe in enumerate(informes):
            print(f"\n--- Informe {i + 1} ---")
            print(f"ID: {informe.get('_id')}")
            print(f"Estudio ID: {informe.get('estudio_id')}")
            print(f"Paciente: {informe.get('paciente_nombre', 'N/A')}")
            print(f"Médico: {informe.get('medico_radiologo')}")

            imagenes = informe.get("imagenes_dicom", [])
            print(f"Imágenes DICOM: {len(imagenes)}")

            for j, imagen in enumerate(imagenes):
                print(f"  Imagen {j + 1}:")
                print(f"    - Archivo DICOM: {imagen.get('archivo_dicom')}")
                print(f"    - Archivo PNG: {imagen.get('archivo_png')}")
                print(f"    - Descripción: {imagen.get('descripcion')}")

        return informes

    except Exception as e:
        print(f"❌ Error buscando informes: {e}")
        return []


async def check_dicom_files(informe):
    """Verificar la existencia de archivos DICOM e imágenes PNG"""
    print(f"\n🔍 Verificando archivos para informe {informe.get('_id')}...")

    estudio_id = informe.get("estudio_id")
    imagenes = informe.get("imagenes_dicom", [])

    if not estudio_id:
        print("❌ No se encontró estudio_id en el informe")
        return False

    upload_dir = Path("backend/uploads/dicom") / estudio_id
    print(f"📁 Directorio del estudio: {upload_dir}")

    if not upload_dir.exists():
        print(f"❌ El directorio del estudio no existe: {upload_dir}")
        return False

    print(f"✅ Directorio existe")

    # Listar todos los archivos en el directorio
    archivos_disponibles = list(upload_dir.glob("*"))
    print(f"📋 Archivos disponibles en el directorio ({len(archivos_disponibles)}):")
    for archivo in archivos_disponibles:
        print(f"  - {archivo.name} ({archivo.stat().st_size} bytes)")

    # Verificar cada imagen del informe
    print(f"\n🔍 Verificando {len(imagenes)} imágenes del informe...")
    resultados = []

    for i, imagen in enumerate(imagenes):
        archivo_dicom = imagen.get("archivo_dicom")
        archivo_png = imagen.get("archivo_png")

        print(f"\n--- Imagen {i + 1} ---")
        print(f"Archivo DICOM esperado: {archivo_dicom}")
        print(f"Archivo PNG esperado: {archivo_png}")

        resultado = {
            "indice": i,
            "archivo_dicom": archivo_dicom,
            "archivo_png": archivo_png,
            "dicom_existe": False,
            "png_existe": False,
            "dicom_valido": False,
            "png_valido": False,
        }

        # Verificar archivo DICOM
        if archivo_dicom:
            dicom_path = upload_dir / archivo_dicom
            if dicom_path.exists():
                resultado["dicom_existe"] = True
                print(f"✅ Archivo DICOM existe ({dicom_path.stat().st_size} bytes)")

                # Intentar leer el archivo DICOM
                try:
                    ds = pydicom.dcmread(str(dicom_path))
                    resultado["dicom_valido"] = True
                    print(f"✅ Archivo DICOM es válido")
                    print(f"   - Modalidad: {ds.get('Modality', 'N/A')}")
                    print(
                        f"   - Dimensiones: {ds.pixel_array.shape if hasattr(ds, 'pixel_array') else 'N/A'}"
                    )
                except Exception as e:
                    print(f"❌ Error leyendo archivo DICOM: {e}")
            else:
                print(f"❌ Archivo DICOM no existe: {dicom_path}")

        # Verificar archivo PNG
        if archivo_png:
            png_path = upload_dir / archivo_png
            if png_path.exists():
                resultado["png_existe"] = True
                print(f"✅ Archivo PNG existe ({png_path.stat().st_size} bytes)")

                # Intentar abrir la imagen PNG
                try:
                    with Image.open(str(png_path)) as img:
                        resultado["png_valido"] = True
                        print(f"✅ Archivo PNG es válido")
                        print(f"   - Dimensiones: {img.size}")
                        print(f"   - Modo: {img.mode}")
                except Exception as e:
                    print(f"❌ Error leyendo archivo PNG: {e}")
            else:
                print(f"❌ Archivo PNG no existe: {png_path}")

        resultados.append(resultado)

    return resultados


def test_dicom_to_png_conversion():
    """Probar la conversión de DICOM a PNG"""
    print("\n🔍 Probando conversión de DICOM a PNG...")

    # Buscar cualquier archivo DICOM en el directorio de uploads
    upload_base = Path("backend/uploads/dicom")

    if not upload_base.exists():
        print(f"❌ Directorio de uploads no existe: {upload_base}")
        return False

    # Buscar archivos DICOM
    dicom_files = list(upload_base.glob("**/*.dcm"))

    if not dicom_files:
        print("❌ No se encontraron archivos DICOM para probar")
        return False

    # Probar con el primer archivo DICOM encontrado
    dicom_file = dicom_files[0]
    print(f"📁 Probando con archivo: {dicom_file}")

    try:
        # Leer archivo DICOM
        ds = pydicom.dcmread(str(dicom_file))
        print(f"✅ Archivo DICOM leído correctamente")

        # Verificar que tiene datos de píxeles
        if not hasattr(ds, "pixel_array"):
            print("❌ El archivo DICOM no contiene datos de píxeles")
            return False

        # Convertir a array numpy
        img_array = ds.pixel_array
        print(f"✅ Datos de píxeles extraídos: {img_array.shape}")

        # Normalizar a 0-255
        normalized = (
            (img_array - np.min(img_array))
            / (np.max(img_array) - np.min(img_array))
            * 255.0
        )
        normalized = normalized.astype(np.uint8)

        # Convertir a imagen PIL
        img = Image.fromarray(normalized)
        print(f"✅ Imagen PIL creada: {img.size}")

        # Guardar como PNG de prueba
        test_png = dicom_file.with_suffix(".test.png")
        img.save(str(test_png), "PNG")
        print(f"✅ Imagen PNG de prueba guardada: {test_png}")

        # Verificar que se puede leer la imagen PNG
        with Image.open(str(test_png)) as test_img:
            print(f"✅ Imagen PNG de prueba verificada: {test_img.size}")

        # Limpiar archivo de prueba
        test_png.unlink()
        print("🧹 Archivo de prueba eliminado")

        return True

    except Exception as e:
        print(f"❌ Error en la conversión: {e}")
        return False


async def simulate_print_request(informe_id):
    """Simular una solicitud de impresión como lo haría el frontend"""
    print(f"\n🖨️ Simulando solicitud de impresión para informe {informe_id}...")

    db = get_database()

    try:
        # Buscar el informe
        informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
        if not informe:
            informe = await db.informes.find_one({"id": informe_id})

        if not informe:
            print(f"❌ Informe no encontrado: {informe_id}")
            return False

        print(f"✅ Informe encontrado")

        # Verificar imágenes
        imagenes = informe.get("imagenes_dicom", [])
        if not imagenes:
            print("ℹ️ El informe no tiene imágenes DICOM")
            return True

        estudio_id = informe.get("estudio_id")
        upload_dir = Path("backend/uploads/dicom") / estudio_id

        print(f"🔍 Simulando carga de {len(imagenes)} imágenes...")

        imagenes_cargadas = 0
        for i, imagen in enumerate(imagenes):
            archivo_png = imagen.get("archivo_png")
            if archivo_png:
                png_path = upload_dir / archivo_png
                if png_path.exists():
                    print(f"✅ Imagen {i + 1} disponible: {archivo_png}")
                    imagenes_cargadas += 1
                else:
                    print(f"❌ Imagen {i + 1} no encontrada: {archivo_png}")
            else:
                print(f"❌ Imagen {i + 1} no tiene archivo_png definido")

        print(f"\n📊 Resumen de carga de imágenes:")
        print(f"   - Total imágenes: {len(imagenes)}")
        print(f"   - Imágenes cargadas: {imagenes_cargadas}")
        print(
            f"   - Porcentaje éxito: {(imagenes_cargadas / len(imagenes) * 100):.1f}%"
        )

        return imagenes_cargadas == len(imagenes)

    except Exception as e:
        print(f"❌ Error simulando impresión: {e}")
        return False


async def main():
    """Función principal del test"""
    print("🧪 === PRUEBA DE FUNCIONALIDAD DE IMPRESIÓN DE INFORMES ===")
    print(f"Timestamp: {datetime.now()}")

    # 1. Probar conexión a BD
    if not await test_database_connection():
        print("❌ No se puede continuar sin conexión a la base de datos")
        return

    # 2. Buscar informes con imágenes
    informes = await find_informes_with_images()
    if not informes:
        print("⚠️ No se encontraron informes con imágenes para probar")
        return

    # 3. Verificar archivos para el primer informe
    primer_informe = informes[0]
    resultados_archivos = await check_dicom_files(primer_informe)

    # 4. Probar conversión DICOM a PNG
    test_dicom_to_png_conversion()

    # 5. Simular solicitud de impresión
    informe_id = str(primer_informe.get("_id"))
    await simulate_print_request(informe_id)

    print("\n🏁 === PRUEBA COMPLETADA ===")

    # Resumen final
    total_imagenes = len(resultados_archivos) if resultados_archivos else 0
    imagenes_ok = (
        sum(1 for r in resultados_archivos if r["png_existe"] and r["png_valido"])
        if resultados_archivos
        else 0
    )

    print(f"\n📊 RESUMEN FINAL:")
    print(f"   - Informes con imágenes encontrados: {len(informes)}")
    print(f"   - Imágenes verificadas: {total_imagenes}")
    print(f"   - Imágenes PNG válidas: {imagenes_ok}")
    print(
        f"   - Tasa de éxito: {(imagenes_ok / total_imagenes * 100):.1f}%"
        if total_imagenes > 0
        else "   - Sin imágenes para verificar"
    )

    if total_imagenes > 0 and imagenes_ok == total_imagenes:
        print("✅ TODAS LAS IMÁGENES ESTÁN DISPONIBLES PARA IMPRESIÓN")
    elif total_imagenes > 0 and imagenes_ok > 0:
        print("⚠️ ALGUNAS IMÁGENES NO ESTÁN DISPONIBLES")
    elif total_imagenes > 0:
        print("❌ NINGUNA IMAGEN ESTÁ DISPONIBLE PARA IMPRESIÓN")
    else:
        print("ℹ️ NO HAY IMÁGENES PARA VERIFICAR")


if __name__ == "__main__":
    # Cambiar al directorio correcto si es necesario
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Ejecutar el test
    asyncio.run(main())
