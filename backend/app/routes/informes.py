from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.database import get_database
from bson import ObjectId
import json

router = APIRouter()

@router.get("/informes/estadisticas")
async def get_estadisticas(inicio: str, fin: str):
    db = get_database()
    
    fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fin, "%Y-%m-%d") + timedelta(days=1)
    
    # Estadísticas de estudios
    pipeline_estudios = [
        {
            "$match": {
                "fecha_solicitud": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$estado",
                "count": {"$sum": 1}
            }
        }
    ]
    
    estudios_por_estado = []
    async for doc in db.estudios.aggregate(pipeline_estudios):
        estudios_por_estado.append({
            "estado": doc["_id"],
            "cantidad": doc["count"]
        })
    
    # Estudios por tipo
    pipeline_tipos = [
        {
            "$match": {
                "fecha_solicitud": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$tipo_estudio",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    estudios_por_tipo = []
    async for doc in db.estudios.aggregate(pipeline_tipos):
        estudios_por_tipo.append({
            "tipo_estudio": doc["_id"],
            "cantidad": doc["count"]
        })
    
    # Citas por estado
    pipeline_citas = [
        {
            "$match": {
                "fecha_creacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$estado",
                "count": {"$sum": 1}
            }
        }
    ]
    
    citas_por_estado = []
    async for doc in db.citas.aggregate(pipeline_citas):
        citas_por_estado.append({
            "estado": doc["_id"],
            "cantidad": doc["count"]
        })
    
    # Tasa de asistencia
    pipeline_asistencia = [
        {
            "$match": {
                "fecha_creacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$asistio",
                "count": {"$sum": 1}
            }
        }
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
        "periodo": {
            "inicio": inicio,
            "fin": fin
        },
        "estudios": {
            "por_estado": estudios_por_estado,
            "por_tipo": estudios_por_tipo,
            "total": sum(item["cantidad"] for item in estudios_por_estado)
        },
        "citas": {
            "por_estado": citas_por_estado,
            "total": total_citas,
            "asistencia": {
                "asistidas": citas_asistidas,
                "no_asistidas": total_citas - citas_asistidas,
                "tasa": round(tasa_asistencia, 2)
            }
        }
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
                "fecha_realizacion": {"$lt": fecha_fin}
            }
        },
        {
            "$project": {
                "tipo_estudio": 1,
                "tiempo_procesamiento": {
                    "$divide": [
                        {"$subtract": ["$fecha_realizacion", "$fecha_solicitud"]},
                        3600000  # Convertir a horas
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$tipo_estudio",
                "tiempo_promedio": {"$avg": "$tiempo_procesamiento"},
                "total_estudios": {"$sum": 1}
            }
        }
    ]
    
    tiempos_estudio = []
    async for doc in db.estudios.aggregate(pipeline_tiempos):
        tiempos_estudio.append({
            "tipo_estudio": doc["_id"],
            "tiempo_promedio_horas": round(doc["tiempo_promedio"], 2),
            "total_estudios": doc["total_estudios"]
        })
    
    # Productividad por técnico
    pipeline_tecnico = [
        {
            "$match": {
                "estado": "completada",
                "fecha_creacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$tecnico_asignado",
                "total_citas": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_citas": -1}
        }
    ]
    
    productividad_tecnico = []
    async for doc in db.citas.aggregate(pipeline_tecnico):
        productividad_tecnico.append({
            "tecnico": doc["_id"],
            "total_citas": doc["total_citas"]
        })
    
    # Utilización de salas
    pipeline_salas = [
        {
            "$match": {
                "fecha_creacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$sala",
                "total_citas": {"$sum": 1},
                "horas_utilizadas": {
                    "$sum": 0.5  # Cada cita dura 30 minutos aprox
                }
            }
        }
    ]
    
    utilizacion_salas = []
    async for doc in db.citas.aggregate(pipeline_salas):
        # 10 horas diarias * días laborales (asumiendo 22 días/mes)
        horas_disponibles = 10 * 22
        utilizacion = (doc["horas_utilizadas"] / horas_disponibles) * 100
        
        utilizacion_salas.append({
            "sala": doc["_id"],
            "total_citas": doc["total_citas"],
            "horas_utilizadas": doc["horas_utilizadas"],
            "utilizacion": round(utilizacion, 2)
        })
    
    return {
        "periodo": {"inicio": inicio, "fin": fin},
        "tiempos_estudio": tiempos_estudio,
        "productividad_tecnico": productividad_tecnico,
        "utilizacion_salas": utilizacion_salas
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
        "Densitometría Ósea": 350000
    }
    
    pipeline_ingresos = [
        {
            "$match": {
                "estado": "completado",
                "fecha_realizacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$group": {
                "_id": "$tipo_estudio",
                "cantidad": {"$sum": 1}
            }
        }
    ]
    
    ingresos = []
    total_ingresos = 0
    
    async for doc in db.estudios.aggregate(pipeline_ingresos):
        precio = precios_estudios.get(doc["_id"], 0)
        ingreso = precio * doc["cantidad"]
        total_ingresos += ingreso
        
        ingresos.append({
            "tipo_estudio": doc["_id"],
            "cantidad": doc["cantidad"],
            "precio_unitario": precio,
            "ingreso_total": ingreso
        })
    
    # Ingresos por mes
    pipeline_mensual = [
        {
            "$match": {
                "estado": "completado",
                "fecha_realizacion": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$project": {
                "year": {"$year": "$fecha_realizacion"},
                "month": {"$month": "$fecha_realizacion"},
                "tipo_estudio": 1
            }
        },
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "month": "$month",
                    "tipo_estudio": "$tipo_estudio"
                },
                "cantidad": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.year": 1, "_id.month": 1}
        }
    ]
    
    ingresos_mensuales = []
    async for doc in db.estudios.aggregate(pipeline_mensual):
        precio = precios_estudios.get(doc["_id"]["tipo_estudio"], 0)
        ingreso = precio * doc["cantidad"]
        
        ingresos_mensuales.append({
            "año": doc["_id"]["year"],
            "mes": doc["_id"]["month"],
            "tipo_estudio": doc["_id"]["tipo_estudio"],
            "cantidad": doc["cantidad"],
            "ingreso": ingreso
        })
    
    return {
        "periodo": {"inicio": inicio, "fin": fin},
        "ingresos_por_estudio": ingresos,
        "ingresos_mensuales": ingresos_mensuales,
        "total_ingresos": total_ingresos
    }

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
        raise HTTPException(status_code=501, detail="Exportación CSV no implementada aún")
    else:
        raise HTTPException(status_code=400, detail="Formato de exportación no válido")
