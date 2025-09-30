from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.schemas import InformeCreate, Informe, InformeUpdate
from app.database import get_database
from bson import ObjectId
from typing import List
import json

router = APIRouter()


@router.get("/informes", response_model=List[Informe])
async def get_informes(skip: int = 0, limit: int = 100):
    """Obtener lista de informes con información del paciente"""
    db = get_database()

    cursor = db.informes.find().skip(skip).limit(limit).sort("fecha_creacion", -1)
    informes = []

    async for informe in cursor:
        # Obtener información del estudio y paciente
        try:
            estudio = await db.estudios.find_one(
                {"_id": ObjectId(informe["estudio_id"])}
            )
            if estudio:
                # Obtener información del paciente
                try:
                    paciente = await db.pacientes.find_one(
                        {"_id": ObjectId(estudio["paciente_id"])}
                    )
                    if paciente:
                        informe["paciente_nombre"] = paciente["nombre"]
                        informe["paciente_apellidos"] = paciente.get("apellidos")
                        informe["paciente_cedula"] = paciente.get("identificacion")
                        informe["paciente_id"] = str(estudio["paciente_id"])
                    else:
                        informe["paciente_nombre"] = "Paciente no encontrado"
                        informe["paciente_apellidos"] = None
                        informe["paciente_cedula"] = None
                        informe["paciente_id"] = str(estudio["paciente_id"])
                except Exception as e:
                    print(f"Error al cargar paciente: {e}")
                    informe["paciente_nombre"] = "Error al cargar paciente"
                    informe["paciente_apellidos"] = None
                    informe["paciente_cedula"] = None
                    informe["paciente_id"] = None

                # Información del estudio
                informe["estudio_tipo"] = estudio.get("tipo_estudio", "No especificado")
                informe["estudio_modalidad"] = estudio.get(
                    "modalidad", "No especificada"
                )
                informe["estudio_fecha"] = estudio.get("fecha_realizacion")
            else:
                informe["paciente_nombre"] = "Estudio no encontrado"
                informe["paciente_apellidos"] = None
                informe["paciente_cedula"] = None
                informe["paciente_id"] = None
                informe["estudio_tipo"] = "No especificado"
                informe["estudio_modalidad"] = "No especificada"
                informe["estudio_fecha"] = None
        except Exception as e:
            print(f"Error al cargar estudio {informe.get('estudio_id')}: {e}")
            informe["paciente_nombre"] = "Error al cargar datos"
            informe["paciente_apellidos"] = None
            informe["paciente_cedula"] = None
            informe["paciente_id"] = None
            informe["estudio_tipo"] = "Error"
            informe["estudio_modalidad"] = "Error"
            informe["estudio_fecha"] = None

        informe["id"] = str(informe["_id"])
        del informe["_id"]
        informes.append(informe)

    return informes


@router.post("/informes", response_model=Informe)
async def create_informe(informe: InformeCreate):
    """Crear un nuevo informe"""
    db = get_database()

    # Convertir a diccionario y agregar timestamps
    informe_dict = informe.dict()
    informe_dict["fecha_creacion"] = datetime.now()
    informe_dict["fecha_actualizacion"] = datetime.now()

    # Insertar en la base de datos
    result = await db.informes.insert_one(informe_dict)

    # Obtener el informe creado
    nuevo_informe = await db.informes.find_one({"_id": result.inserted_id})
    nuevo_informe["id"] = str(nuevo_informe["_id"])
    del nuevo_informe["_id"]

    return Informe(**nuevo_informe)


@router.get("/informes/{informe_id}", response_model=Informe)
async def get_informe(informe_id: str):
    """Obtener un informe por ID"""
    try:
        db = get_database()
        informe = await db.informes.find_one({"_id": ObjectId(informe_id)})

        if not informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")

        informe["id"] = str(informe["_id"])
        del informe["_id"]

        return Informe(**informe)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de informe inválido")


@router.put("/informes/{informe_id}", response_model=Informe)
async def update_informe(informe_id: str, informe: InformeUpdate):
    """Actualizar un informe"""
    try:
        db = get_database()

        # Verificar que el informe existe
        existing_informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
        if not existing_informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")

        # Preparar datos para actualizar
        update_data = informe.dict(exclude_unset=True)
        update_data["fecha_actualizacion"] = datetime.now()

        # Actualizar en la base de datos
        result = await db.informes.update_one(
            {"_id": ObjectId(informe_id)}, {"$set": update_data}
        )

        if result.modified_count == 1:
            # Obtener el informe actualizado
            updated_informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
            updated_informe["id"] = str(updated_informe["_id"])
            del updated_informe["_id"]

            return Informe(**updated_informe)
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar el informe"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de informe inválido")


@router.delete("/informes/{informe_id}")
async def delete_informe(informe_id: str):
    """Eliminar un informe"""
    try:
        db = get_database()

        # Verificar que el informe existe
        existing_informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
        if not existing_informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")

        # Eliminar el informe
        result = await db.informes.delete_one({"_id": ObjectId(informe_id)})

        if result.deleted_count == 1:
            return {"message": "Informe eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar el informe")

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de informe inválido")


@router.get("/informes/estadisticas")
async def get_estadisticas(inicio: str, fin: str):
    db = get_database()

    fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fin, "%Y-%m-%d") + timedelta(days=1)

    # Estadísticas de estudios
    pipeline_estudios = [
        {"$match": {"fecha_solicitud": {"$gte": fecha_inicio, "$lt": fecha_fin}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
    ]

    estudios_por_estado = []
    async for doc in db.estudios.aggregate(pipeline_estudios):
        estudios_por_estado.append({"estado": doc["_id"], "cantidad": doc["count"]})

    # Estudios por tipo
    pipeline_tipos = [
        {"$match": {"fecha_solicitud": {"$gte": fecha_inicio, "$lt": fecha_fin}}},
        {"$group": {"_id": "$tipo_estudio", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    estudios_por_tipo = []
    async for doc in db.estudios.aggregate(pipeline_tipos):
        estudios_por_tipo.append({"tipo_estudio": doc["_id"], "cantidad": doc["count"]})

    # Citas por estado
    pipeline_citas = [
        {"$match": {"fecha_creacion": {"$gte": fecha_inicio, "$lt": fecha_fin}}},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
    ]

    citas_por_estado = []
    async for doc in db.citas.aggregate(pipeline_citas):
        citas_por_estado.append({"estado": doc["_id"], "cantidad": doc["count"]})

    # Tasa de asistencia
    pipeline_asistencia = [
        {"$match": {"fecha_creacion": {"$gte": fecha_inicio, "$lt": fecha_fin}}},
        {"$group": {"_id": "$asistio", "count": {"$sum": 1}}},
    ]

    asistencia_data = []
    total_citas = 0
    citas_asistidas = 0

    async for doc in db.citas.aggregate(pipeline_asistencia):
        total_citas += doc["count"]
        if doc["_id"] == True:
            citas_asistidas = doc["count"]

    tasa_asistencia = (citas_asistidas / total_citas * 100) if total_citas > 0 else 0

    return {
        "periodo": {"inicio": inicio, "fin": fin},
        "estudios": {
            "por_estado": estudios_por_estado,
            "por_tipo": estudios_por_tipo,
            "total": sum(item["cantidad"] for item in estudios_por_estado),
        },
        "citas": {
            "por_estado": citas_por_estado,
            "total": total_citas,
            "asistencia": {
                "asistidas": citas_asistidas,
                "no_asistidas": total_citas - citas_asistidas,
                "tasa": round(tasa_asistencia, 2),
            },
        },
    }


@router.get("/informes/rendimiento")
async def get_informe_rendimiento(inicio: str, fin: str):
    db = get_database()

    fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fin, "%Y-%m-%d") + timedelta(days=1)

    # Tiempos promedio por estudio
    pipeline_tiempos = [
        {
            "$match": {
                "estado": "completado",
                "fecha_solicitud": {"$gte": fecha_inicio},
                "fecha_realizacion": {"$lt": fecha_fin},
            }
        },
        {
            "$project": {
                "tipo_estudio": 1,
                "tiempo_procesamiento": {
                    "$divide": [
                        {"$subtract": ["$fecha_realizacion", "$fecha_solicitud"]},
                        3600000,  # Convertir a horas
                    ]
                },
            }
        },
        {
            "$group": {
                "_id": "$tipo_estudio",
                "tiempo_promedio": {"$avg": "$tiempo_procesamiento"},
                "total_estudios": {"$sum": 1},
            }
        },
    ]

    tiempos_estudio = []
    async for doc in db.estudios.aggregate(pipeline_tiempos):
        tiempos_estudio.append(
            {
                "tipo_estudio": doc["_id"],
                "tiempo_promedio_horas": round(doc["tiempo_promedio"], 2),
                "total_estudios": doc["total_estudios"],
            }
        )

    # Productividad por técnico
    pipeline_tecnico = [
        {
            "$match": {
                "estado": "completada",
                "fecha_creacion": {"$gte": fecha_inicio, "$lt": fecha_fin},
            }
        },
        {"$group": {"_id": "$tecnico_asignado", "total_citas": {"$sum": 1}}},
        {"$sort": {"total_citas": -1}},
    ]

    productividad_tecnico = []
    async for doc in db.citas.aggregate(pipeline_tecnico):
        productividad_tecnico.append(
            {"tecnico": doc["_id"], "total_citas": doc["total_citas"]}
        )

    # Utilización de salas
    pipeline_salas = [
        {"$match": {"fecha_creacion": {"$gte": fecha_inicio, "$lt": fecha_fin}}},
        {
            "$group": {
                "_id": "$sala",
                "total_citas": {"$sum": 1},
                "horas_utilizadas": {
                    "$sum": 0.5  # Cada cita dura 30 minutos aprox
                },
            }
        },
    ]

    utilizacion_salas = []
    async for doc in db.citas.aggregate(pipeline_salas):
        # 10 horas diarias * días laborales (asumiendo 22 días/mes)
        horas_disponibles = 10 * 22
        utilizacion = (doc["horas_utilizadas"] / horas_disponibles) * 100

        utilizacion_salas.append(
            {
                "sala": doc["_id"],
                "total_citas": doc["total_citas"],
                "horas_utilizadas": doc["horas_utilizadas"],
                "utilizacion": round(utilizacion, 2),
            }
        )

    return {
        "periodo": {"inicio": inicio, "fin": fin},
        "tiempos_estudio": tiempos_estudio,
        "productividad_tecnico": productividad_tecnico,
        "utilizacion_salas": utilizacion_salas,
    }


@router.get("/informes/financiero")
async def get_informe_financiero(inicio: str, fin: str):
    db = get_database()

    fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fin, "%Y-%m-%d") + timedelta(days=1)

    # Precios por tipo de estudio (esto debería venir de una base de datos)
    precios_estudios = {
        "Radiografía de Tórax": 150000,
        "Resonancia Magnética": 800000,
        "Tomografía Computarizada": 600000,
        "Ultrasonido Abdominal": 300000,
        "Mamografía": 250000,
        "Densitometría Ósea": 350000,
    }

    pipeline_ingresos = [
        {
            "$match": {
                "estado": "completado",
                "fecha_realizacion": {"$gte": fecha_inicio, "$lt": fecha_fin},
            }
        },
        {"$group": {"_id": "$tipo_estudio", "cantidad": {"$sum": 1}}},
    ]

    ingresos = []
    total_ingresos = 0

    async for doc in db.estudios.aggregate(pipeline_ingresos):
        precio = precios_estudios.get(doc["_id"], 0)
        ingreso = precio * doc["cantidad"]
        total_ingresos += ingreso

        ingresos.append(
            {
                "tipo_estudio": doc["_id"],
                "cantidad": doc["cantidad"],
                "precio_unitario": precio,
                "ingreso_total": ingreso,
            }
        )

    # Ingresos por mes
    pipeline_mensual = [
        {
            "$match": {
                "estado": "completado",
                "fecha_realizacion": {"$gte": fecha_inicio, "$lt": fecha_fin},
            }
        },
        {
            "$project": {
                "year": {"$year": "$fecha_realizacion"},
                "month": {"$month": "$fecha_realizacion"},
                "tipo_estudio": 1,
            }
        },
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "month": "$month",
                    "tipo_estudio": "$tipo_estudio",
                },
                "cantidad": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]

    ingresos_mensuales = []
    async for doc in db.estudios.aggregate(pipeline_mensual):
        precio = precios_estudios.get(doc["_id"]["tipo_estudio"], 0)
        ingreso = precio * doc["cantidad"]

        ingresos_mensuales.append(
            {
                "año": doc["_id"]["year"],
                "mes": doc["_id"]["month"],
                "tipo_estudio": doc["_id"]["tipo_estudio"],
                "cantidad": doc["cantidad"],
                "ingreso": ingreso,
            }
        )

    return {
        "periodo": {"inicio": inicio, "fin": fin},
        "ingresos_por_estudio": ingresos,
        "ingresos_mensuales": ingresos_mensuales,
        "total_ingresos": total_ingresos,
    }


@router.get("/informes/{informe_id}/debug/imagenes")
async def debug_imagenes_informe(informe_id: str):
    """Debug endpoint para verificar el estado de las imágenes DICOM en un informe"""
    try:
        db = get_database()

        # Buscar informe por ID
        informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
        if not informe:
            # Intentar buscar por campo id
            informe = await db.informes.find_one({"id": informe_id})

        if not informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")

        # Extraer información de imágenes
        imagenes_dicom = informe.get("imagenes_dicom", [])

        # Verificar existencia de archivos en el sistema
        import os

        UPLOAD_DIR = "uploads/dicom"
        estudio_id = informe.get("estudio_id")

        debug_info = {
            "informe_id": str(informe.get("_id")),
            "estudio_id": estudio_id,
            "total_imagenes": len(imagenes_dicom),
            "imagenes": [],
        }

        for i, imagen in enumerate(imagenes_dicom):
            archivo_png = imagen.get("archivo_png")
            archivo_dicom = imagen.get("archivo_dicom")

            # Verificar si los archivos existen
            png_path = (
                os.path.join(UPLOAD_DIR, estudio_id, archivo_png)
                if archivo_png
                else None
            )
            dicom_path = (
                os.path.join(UPLOAD_DIR, estudio_id, archivo_dicom)
                if archivo_dicom
                else None
            )

            imagen_info = {
                "indice": i,
                "archivo_dicom": archivo_dicom,
                "archivo_png": archivo_png,
                "descripcion": imagen.get("descripcion"),
                "orden": imagen.get("orden"),
                "png_existe": os.path.exists(png_path) if png_path else False,
                "dicom_existe": os.path.exists(dicom_path) if dicom_path else False,
                "png_path": png_path,
                "dicom_path": dicom_path,
            }

            debug_info["imagenes"].append(imagen_info)

        # Verificar directorio del estudio
        study_dir = os.path.join(UPLOAD_DIR, estudio_id) if estudio_id else None
        if study_dir and os.path.exists(study_dir):
            archivos_disponibles = os.listdir(study_dir)
            debug_info["archivos_en_directorio"] = archivos_disponibles
        else:
            debug_info["archivos_en_directorio"] = []
            debug_info["directorio_existe"] = False

        return debug_info

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de informe inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/informes/{informe_id}/sync-imagenes")
async def sync_imagenes_informe(informe_id: str):
    """Sincroniza imagenes_dicom del informe desde los archivos del estudio asociado."""
    try:
        db = get_database()

        # Buscar informe por _id o id
        informe = await db.informes.find_one({"_id": ObjectId(informe_id)})
        if not informe:
            informe = await db.informes.find_one({"id": informe_id})
        if not informe:
            raise HTTPException(status_code=404, detail="Informe no encontrado")

        estudio_id = informe.get("estudio_id")
        if not estudio_id:
            raise HTTPException(status_code=400, detail="Informe sin estudio asociado")

        # Obtener estudio por id o _id
        estudio = await db.estudios.find_one({"id": estudio_id})
        if not estudio:
            try:
                estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
            except Exception:
                estudio = None
        if not estudio:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        archivos = estudio.get("archivos_dicom", [])
        if not archivos:
            return {"message": "El estudio no tiene archivos DICOM", "sincronizadas": 0}

        # Construir imagenes_dicom a partir de archivos del estudio
        imagenes = []
        for idx, a in enumerate(archivos):
            saved = a.get("saved_name")
            preview = a.get("preview_name")
            png = preview or (saved.replace(".dcm", ".png") if saved else None)
            if not png:
                continue
            imagenes.append(
                {
                    "archivo_dicom": saved,
                    "archivo_png": png,
                    "estudio_id": estudio_id,
                    "descripcion": f"Imagen {idx + 1} - {a.get('original_name', 'DICOM')}",
                    "orden": idx,
                }
            )

        if not imagenes:
            return {"message": "No se generaron imágenes a anexar", "sincronizadas": 0}

        filtro = {"_id": informe.get("_id")} if informe.get("_id") else {"id": informe.get("id")}
        await db.informes.update_one(
            filtro,
            {"$set": {"imagenes_dicom": imagenes, "fecha_actualizacion": datetime.now()}},
        )

        return {"message": "Imágenes sincronizadas", "sincronizadas": len(imagenes)}
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de informe inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/informes/export/{tipo}")
async def exportar_informe(tipo: str, inicio: str, fin: str, formato: str = "json"):
    if tipo == "estadisticas":
        data = await get_estadisticas(inicio, fin)
    elif tipo == "rendimiento":
        data = await get_informe_rendimiento(inicio, fin)
    elif tipo == "financiero":
        data = await get_informe_financiero(inicio, fin)
    else:
        raise HTTPException(status_code=400, detail="Tipo de informe no válido")

    if formato == "json":
        return data
    elif formato == "csv":
        # Implementar conversión a CSV
        raise HTTPException(
            status_code=501, detail="Exportación CSV no implementada aún"
        )
    else:
        raise HTTPException(status_code=400, detail="Formato de exportación no válido")
