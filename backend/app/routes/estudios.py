from fastapi import APIRouter, HTTPException
from app.schemas import EstudioCreate, Estudio, EstudioUpdate
from app.database import get_database
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List

router = APIRouter()


@router.get("/estudios", response_model=List[Estudio])
async def get_estudios(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    tipo_estudio: str = None,
    paciente_id: str = None,
    medico_solicitante: str = None,
    prioridad: str = None,
    fecha_solicitud: str = None,
    fecha_realizacion: str = None,
    paciente_nombre: str = None,
):
    """Obtener lista de estudios con filtros opcionales"""
    db = get_database()
    query = {}

    # Filtro por estado (convertir a minúsculas para consistencia)
    if estado and estado != "Todos":
        query["estado"] = estado.lower().replace(" ", "_")

    # Filtro por tipo de estudio
    if tipo_estudio and tipo_estudio != "Todos":
        query["tipo_estudio"] = {"$regex": tipo_estudio, "$options": "i"}

    # Filtro por paciente específico
    if paciente_id:
        query["paciente_id"] = paciente_id

    # Filtro por médico solicitante
    if medico_solicitante and medico_solicitante != "Todos":
        query["medico_solicitante"] = {"$regex": medico_solicitante, "$options": "i"}

    # Filtro por prioridad
    if prioridad and prioridad != "Todos":
        query["prioridad"] = prioridad.lower()

    # Filtro por fecha de solicitud
    if fecha_solicitud:
        try:
            fecha_obj = datetime.strptime(fecha_solicitud, "%Y-%m-%d")
            inicio_dia = datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day)
            fin_dia = inicio_dia + timedelta(days=1)
            query["fecha_solicitud"] = {"$gte": inicio_dia, "$lt": fin_dia}
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD"
            )

    # Filtro por fecha de realización
    if fecha_realizacion:
        try:
            fecha_obj = datetime.strptime(fecha_realizacion, "%Y-%m-%d")
            inicio_dia = datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day)
            fin_dia = inicio_dia + timedelta(days=1)
            query["fecha_realizacion"] = {"$gte": inicio_dia, "$lt": fin_dia}
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha de realización inválido. Use YYYY-MM-DD",
            )

    # Aplicar filtro por nombre de paciente en la consulta de MongoDB si se especifica
    if paciente_nombre:
        # Buscar pacientes que coincidan con el nombre
        nombre_regex = {"$regex": paciente_nombre, "$options": "i"}
        pacientes_coincidentes = db.pacientes.find(
            {"$or": [{"nombre": nombre_regex}, {"apellidos": nombre_regex}]}
        )

        pacientes_ids = []
        async for p in pacientes_coincidentes:
            pacientes_ids.append(str(p["_id"]))

        if pacientes_ids:
            query["paciente_id"] = {"$in": pacientes_ids}
        else:
            # Si no hay pacientes que coincidan, retornar lista vacía
            return []

    estudios = []
    async for estudio in (
        db.estudios.find(query).skip(skip).limit(limit).sort("fecha_solicitud", -1)
    ):
        # Obtener información del paciente
        try:
            # Try to find patient by _id or id
            paciente = None
            try:
                paciente = await db.pacientes.find_one(
                    {"_id": ObjectId(estudio["paciente_id"])}
                )
            except:
                paciente = await db.pacientes.find_one({"id": estudio["paciente_id"]})

            if paciente:
                estudio["paciente_nombre"] = paciente.get("nombre", "")
                estudio["paciente_apellidos"] = paciente.get("apellidos", "")
                estudio["paciente_cedula"] = paciente.get("identificacion", "")
                # Calcular edad si existe fecha_nacimiento
                if paciente.get("fecha_nacimiento"):
                    from datetime import datetime

                    try:
                        if isinstance(paciente["fecha_nacimiento"], str):
                            fecha_nac = datetime.fromisoformat(
                                paciente["fecha_nacimiento"].replace("Z", "+00:00")
                            )
                        else:
                            fecha_nac = paciente["fecha_nacimiento"]
                        edad = (datetime.now() - fecha_nac).days // 365
                        estudio["paciente_edad"] = edad
                    except:
                        estudio["paciente_edad"] = None
                else:
                    estudio["paciente_edad"] = None
            else:
                print(f"Paciente no encontrado para ID: {estudio['paciente_id']}")
                estudio["paciente_nombre"] = "Paciente no encontrado"
                estudio["paciente_apellidos"] = ""
                estudio["paciente_cedula"] = ""
                estudio["paciente_edad"] = None
        except Exception as e:
            print(f"Error al cargar paciente {estudio.get('paciente_id')}: {e}")
            estudio["paciente_nombre"] = "Error al cargar paciente"
            estudio["paciente_apellidos"] = ""
            estudio["paciente_cedula"] = ""
            estudio["paciente_edad"] = None

        # Mantener estado en formato interno (enum esperado por schema)
        # Si se requiere una etiqueta amigable para el frontend, devolver en otro campo opcional
        estudio["estado_display"] = estudio["estado"].replace("_", " ").title()
        if estudio["estado_display"] == "En Proceso":
            estudio["estado_display"] = "En Proceso"

        # Normalizar prioridad para el frontend
        if estudio.get("prioridad"):
            if estudio["prioridad"] in ["alta", "urgente"]:
                estudio["prioridad"] = "Urgente"
            elif estudio["prioridad"] == "normal":
                estudio["prioridad"] = "Normal"
            else:
                estudio["prioridad"] = estudio["prioridad"].title()

        estudio["id"] = str(estudio["_id"])
        del estudio["_id"]
        estudios.append(estudio)

    return estudios


@router.get("/estudios/{estudio_id}", response_model=Estudio)
async def get_estudio(estudio_id: str):
    """Obtener un estudio específico por ID"""
    try:
        db = get_database()
        estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})

        if estudio:
            # Obtener información del paciente
            try:
                paciente = await db.pacientes.find_one(
                    {"_id": ObjectId(estudio["paciente_id"])}
                )
                if paciente:
                    estudio["paciente_nombre"] = paciente["nombre"]
                    estudio["paciente_apellidos"] = paciente.get("apellidos")
                    estudio["paciente_cedula"] = paciente.get("cedula")
                    estudio["paciente_edad"] = paciente.get("edad")
                else:
                    estudio["paciente_nombre"] = "Paciente no encontrado"
                    estudio["paciente_apellidos"] = None
                    estudio["paciente_cedula"] = None
                    estudio["paciente_edad"] = None
            except Exception as e:
                print(f"Error al cargar paciente {estudio.get('paciente_id')}: {e}")
                estudio["paciente_nombre"] = "Error al cargar paciente"
                estudio["paciente_apellidos"] = None
                estudio["paciente_cedula"] = None
                estudio["paciente_edad"] = None

            estudio["id"] = str(estudio["_id"])
            del estudio["_id"]
            return estudio
        else:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")
    except Exception as e:
        print(f"Error general en get_estudio: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/pacientes/{paciente_id}/estudios", response_model=List[Estudio])
async def get_estudios_paciente(paciente_id: str):
    """Obtener todos los estudios de un paciente específico"""
    try:
        db = get_database()

        # Verificar que el paciente existe
        paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        estudios = []
        async for estudio in db.estudios.find({"paciente_id": paciente_id}).sort(
            "fecha_solicitud", -1
        ):
            estudio["id"] = str(estudio["_id"])
            estudios.append(Estudio(**estudio))

        return estudios
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")


@router.post("/estudios", response_model=Estudio)
async def create_estudio(estudio: EstudioCreate):
    """Crear un nuevo estudio"""
    try:
        db = get_database()

        # Verificar que el paciente existe
        paciente = await db.pacientes.find_one({"_id": ObjectId(estudio.paciente_id)})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        estudio_dict = estudio.dict()
        estudio_dict["estado"] = "pendiente"
        estudio_dict["fecha_solicitud"] = datetime.now()
        estudio_dict["fecha_actualizacion"] = datetime.now()
        estudio_dict["archivos_dicom"] = []

        result = await db.estudios.insert_one(estudio_dict)
        new_estudio = await db.estudios.find_one({"_id": result.inserted_id})

        new_estudio["id"] = str(new_estudio["_id"])
        return Estudio(**new_estudio)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")


@router.put("/estudios/{estudio_id}", response_model=Estudio)
async def update_estudio(estudio_id: str, estudio: EstudioUpdate):
    """Actualizar un estudio existente"""
    try:
        db = get_database()

        # Verificar que el estudio existe
        existing_study = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not existing_study:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        # Preparar datos de actualización
        update_data = {}
        for field, value in estudio.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=400, detail="No se proporcionaron datos para actualizar"
            )

        update_data["fecha_actualizacion"] = datetime.now()

        # Si se está marcando como completado, agregar fecha de realización
        if update_data.get("estado") == "completado":
            update_data["fecha_realizacion"] = datetime.now()

        result = await db.estudios.update_one(
            {"_id": ObjectId(estudio_id)}, {"$set": update_data}
        )

        if result.modified_count == 1:
            updated_estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
            updated_estudio["id"] = str(updated_estudio["_id"])
            return Estudio(**updated_estudio)
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar el estudio"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")


@router.put("/estudios/{estudio_id}/estado", response_model=Estudio)
async def update_estado_estudio(estudio_id: str, estado: str):
    """Actualizar solo el estado de un estudio"""
    try:
        db = get_database()

        # Verificar que el estudio existe
        existing_study = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not existing_study:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        # Validar estado
        estados_validos = [
            "pendiente",
            "programado",
            "en_proceso",
            "completado",
            "cancelado",
        ]
        if estado not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Estados válidos: {estados_validos}",
            )

        update_data = {"estado": estado, "fecha_actualizacion": datetime.now()}

        # Si se está marcando como completado, agregar fecha de realización
        if estado == "completado":
            update_data["fecha_realizacion"] = datetime.now()

        result = await db.estudios.update_one(
            {"_id": ObjectId(estudio_id)}, {"$set": update_data}
        )

        if result.modified_count == 1:
            updated_estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
            updated_estudio["id"] = str(updated_estudio["_id"])
            return Estudio(**updated_estudio)
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar el estado del estudio"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")


@router.put("/estudios/{estudio_id}/resultados", response_model=Estudio)
async def add_resultados_estudio(estudio_id: str, resultados: str):
    """Agregar resultados a un estudio"""
    try:
        db = get_database()

        # Verificar que el estudio existe
        existing_study = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not existing_study:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        result = await db.estudios.update_one(
            {"_id": ObjectId(estudio_id)},
            {"$set": {"resultados": resultados, "fecha_actualizacion": datetime.now()}},
        )

        if result.modified_count == 1:
            updated_estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
            updated_estudio["id"] = str(updated_estudio["_id"])
            return Estudio(**updated_estudio)
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar los resultados del estudio"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")


@router.delete("/estudios/{estudio_id}")
async def delete_estudio(estudio_id: str):
    """Eliminar un estudio (soft delete)"""
    try:
        db = get_database()

        # Verificar que el estudio existe
        existing_study = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not existing_study:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        # Verificar que no tenga citas programadas
        active_appointments = await db.citas.count_documents(
            {"estudio_id": estudio_id, "estado": {"$in": ["programada", "en_proceso"]}}
        )

        if active_appointments > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el estudio porque tiene citas programadas",
            )

        # Soft delete: marcar como cancelado
        result = await db.estudios.update_one(
            {"_id": ObjectId(estudio_id)},
            {"$set": {"estado": "cancelado", "fecha_actualizacion": datetime.now()}},
        )

        if result.modified_count == 1:
            return {"message": "Estudio marcado como cancelado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al cancelar el estudio")

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")
