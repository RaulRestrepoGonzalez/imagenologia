from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timedelta
from app.schemas import CitaCreate, Cita, CitaUpdate
from app.database import get_database
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from bson import ObjectId
from typing import List

router = APIRouter()
email_service = EmailService()
sms_service = SMSService()


async def send_appointment_notifications(
    email: str, telefono: str, fecha_cita: datetime, tipo_estudio: str
):
    """Enviar notificaciones de cita por email y SMS"""
    try:
        # Formatear fecha para mostrar
        fecha_formateada = fecha_cita.strftime("%d/%m/%Y a las %H:%M")

        # Enviar email solo si el servicio está configurado
        if email:
            try:
                subject = "Confirmación de Cita - Imagenología"
                body = f"""
                Estimado paciente,

                Su cita ha sido programada exitosamente:

                Fecha y Hora: {fecha_formateada}
                Tipo de Estudio: {tipo_estudio}

                Por favor, llegue 15 minutos antes de su cita.

                Saludos,
                Centro de Imagenología
                """
                await email_service.send_email(email, subject, body)
                print(f"Email enviado a {email}")
            except Exception as e:
                print(f"No se pudo enviar email (servicio no configurado): {e}")

        # Enviar SMS solo si el servicio está configurado
        if telefono:
            try:
                mensaje = f"Cita confirmada: {tipo_estudio} el {fecha_formateada}. Centro de Imagenología."
                await sms_service.send_sms(telefono, mensaje)
                print(f"SMS enviado a {telefono}")
            except Exception as e:
                print(f"No se pudo enviar SMS (servicio no configurado): {e}")

    except Exception as e:
        print(f"Error general enviando notificaciones: {e}")


@router.get("/citas", response_model=List[Cita])
async def get_citas(
    fecha: str = None,
    estado: str = None,
    tipo_estudio: str = None,
    tipo_cita: str = None,
    paciente_nombre: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """Obtener lista de citas con filtros opcionales"""
    db = get_database()
    query = {}

    # Filtro por fecha
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            inicio_dia = datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day)
            fin_dia = inicio_dia + timedelta(days=1)
            query["fecha_cita"] = {"$gte": inicio_dia, "$lt": fin_dia}
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD"
            )

    # Filtro por estado (convertir a minúsculas para consistencia)
    if estado and estado != "Todos":
        query["estado"] = estado.lower()

    # Filtro por tipo de estudio
    if tipo_estudio and tipo_estudio != "Todos":
        query["tipo_estudio"] = {"$regex": tipo_estudio, "$options": "i"}

    # Filtro por tipo de cita (nuevo)
    if tipo_cita and tipo_cita != "Todos":
        query["tipo_cita"] = {"$regex": tipo_cita, "$options": "i"}

    citas = []
    cursor = db.citas.find(query).skip(skip).limit(limit).sort("fecha_cita", 1)

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

    # Ejecutar consulta con filtros aplicados
    cursor = db.citas.find(query).skip(skip).limit(limit).sort("fecha_cita", 1)

    async for cita in cursor:
        # Obtener información del paciente
        paciente = await db.pacientes.find_one({"_id": ObjectId(cita["paciente_id"])})
        if paciente:
            cita["paciente_nombre"] = paciente["nombre"]
            cita["paciente_apellidos"] = paciente.get("apellidos", "")
        else:
            cita["paciente_nombre"] = "Desconocido"
            cita["paciente_apellidos"] = ""

        # Agregar tipo_cita si no existe
        if "tipo_cita" not in cita:
            cita["tipo_cita"] = "Consulta General"

        # Agregar campos de médico y sala si no existen
        if "medico_asignado" not in cita:
            cita["medico_asignado"] = None
        if "sala" not in cita:
            cita["sala"] = None

        # Normalizar estado para el frontend
        estado_normalizado = cita["estado"].replace("_", " ").title()
        if estado_normalizado == "No Asistio":
            estado_normalizado = "No Asistió"
        cita["estado"] = estado_normalizado

        cita["id"] = str(cita["_id"])
        del cita["_id"]
        citas.append(Cita(**cita))

    return citas


@router.get("/citas/{cita_id}", response_model=Cita)
async def get_cita(cita_id: str):
    """Obtener una cita específica por ID"""
    try:
        db = get_database()
        cita = await db.citas.find_one({"_id": ObjectId(cita_id)})

        if cita:
            cita["id"] = str(cita["_id"])
            return Cita(**cita)
        else:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cita inválido")


@router.get("/estudios/{estudio_id}/citas", response_model=List[Cita])
async def get_citas_estudio(estudio_id: str):
    """Obtener todas las citas de un estudio específico"""
    try:
        db = get_database()

        # Verificar que el estudio existe
        estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not estudio:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")

        citas = []
        async for cita in db.citas.find({"estudio_id": estudio_id}).sort(
            "fecha_hora", 1
        ):
            cita["id"] = str(cita["_id"])
            citas.append(Cita(**cita))

        return citas
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")


@router.post("/citas", response_model=Cita)
async def create_cita(cita: CitaCreate, background_tasks: BackgroundTasks):
    """Crear una nueva cita"""
    db = get_database()

    # Verificar que el paciente existe
    paciente = await db.pacientes.find_one({"_id": ObjectId(cita.paciente_id)})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Crear la cita
    cita_dict = cita.dict()
    cita_dict["fecha_creacion"] = datetime.now()
    cita_dict["fecha_actualizacion"] = datetime.now()

    result = await db.citas.insert_one(cita_dict)
    nueva_cita = await db.citas.find_one({"_id": result.inserted_id})
    nueva_cita["id"] = str(nueva_cita["_id"])
    nueva_cita["paciente_nombre"] = paciente["nombre"]
    nueva_cita["paciente_apellidos"] = paciente.get("apellidos")
    del nueva_cita["_id"]

    # Enviar notificaciones
    if paciente.get("email"):
        background_tasks.add_task(
            send_appointment_notifications,
            paciente["email"],
            paciente.get("telefono"),
            nueva_cita["fecha_cita"],
            nueva_cita["tipo_estudio"],
        )

    return Cita(**nueva_cita)


@router.put("/citas/{cita_id}", response_model=Cita)
async def update_cita(cita_id: str, cita: CitaUpdate):
    """Actualizar una cita existente"""
    try:
        db = get_database()

        # Verificar que la cita existe
        existing_appointment = await db.citas.find_one({"_id": ObjectId(cita_id)})
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Preparar datos de actualización
        update_data = {}
        for field, value in cita.dict(exclude_unset=True).items():
            if value is not None:
                # Normalizar estado a minúsculas para la base de datos
                if field == "estado":
                    update_data[field] = (
                        value.lower().replace(" ", "_").replace("ó", "o")
                    )
                else:
                    update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=400, detail="No se proporcionaron datos para actualizar"
            )

        update_data["fecha_actualizacion"] = datetime.now()

        # Si se está cambiando la fecha/hora, verificar disponibilidad
        if "fecha_hora" in update_data:
            cita_existente = await db.citas.find_one(
                {
                    "fecha_hora": update_data["fecha_hora"],
                    "_id": {"$ne": ObjectId(cita_id)},
                    "$or": [
                        {"sala": update_data.get("sala", existing_appointment["sala"])},
                        {
                            "tecnico_asignado": update_data.get(
                                "tecnico_asignado",
                                existing_appointment["tecnico_asignado"],
                            )
                        },
                    ],
                }
            )

            if cita_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Conflicto de horario: sala o técnico no disponible",
                )

        result = await db.citas.update_one(
            {"_id": ObjectId(cita_id)}, {"$set": update_data}
        )

        if result.modified_count == 1:
            updated_cita = await db.citas.find_one({"_id": ObjectId(cita_id)})

            # Obtener información del paciente
            paciente = await db.pacientes.find_one(
                {"_id": ObjectId(updated_cita["paciente_id"])}
            )
            if paciente:
                updated_cita["paciente_nombre"] = paciente["nombre"]
                updated_cita["paciente_apellidos"] = paciente.get("apellidos", "")

            # Normalizar estado para el frontend
            estado_normalizado = updated_cita["estado"].replace("_", " ").title()
            if estado_normalizado == "No Asistio":
                estado_normalizado = "No Asistió"
            updated_cita["estado"] = estado_normalizado

            updated_cita["id"] = str(updated_cita["_id"])
            del updated_cita["_id"]
            return Cita(**updated_cita)
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar la cita")

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cita inválido")


@router.delete("/citas/{cita_id}")
async def delete_cita(cita_id: str):
    """Cancelar una cita"""
    try:
        db = get_database()

        # Verificar que la cita existe
        existing_appointment = await db.citas.find_one({"_id": ObjectId(cita_id)})
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Solo se pueden cancelar citas que no estén ya canceladas o completadas
        if existing_appointment["estado"] in ["cancelada", "completada"]:
            raise HTTPException(
                status_code=400,
                detail="No se puede cancelar una cita ya cancelada o completada",
            )

        # Marcar cita como cancelada
        result = await db.citas.update_one(
            {"_id": ObjectId(cita_id)},
            {"$set": {"estado": "cancelada", "fecha_actualizacion": datetime.now()}},
        )

        if result.modified_count == 1:
            # Actualizar estado del estudio si existe estudio_id
            if existing_appointment.get("estudio_id"):
                try:
                    await db.estudios.update_one(
                        {"_id": ObjectId(existing_appointment["estudio_id"])},
                        {
                            "$set": {
                                "estado": "pendiente",
                                "fecha_actualizacion": datetime.now(),
                            }
                        },
                    )
                except Exception as e:
                    print(f"Error actualizando estudio: {e}")

            return {"message": "Cita cancelada correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al cancelar la cita")

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cita inválido")


@router.put("/citas/{cita_id}/asistencia")
async def update_asistencia_cita(cita_id: str, asistio: bool):
    """Actualizar la asistencia de una cita"""
    try:
        db = get_database()

        # Verificar que la cita existe
        existing_appointment = await db.citas.find_one({"_id": ObjectId(cita_id)})
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Solo se puede actualizar asistencia de citas en proceso o completadas
        if existing_appointment["estado"] not in ["programada", "completada"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se puede actualizar asistencia de citas programadas o completadas",
            )

        update_data = {"asistio": asistio, "fecha_actualizacion": datetime.now()}

        # Si no asistió, marcar como no asistió
        if not asistio:
            update_data["estado"] = "no_asistio"

        result = await db.citas.update_one(
            {"_id": ObjectId(cita_id)}, {"$set": update_data}
        )

        if result.modified_count == 1:
            return {"message": "Asistencia actualizada correctamente"}
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar la asistencia"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cita inválido")


async def enviar_confirmacion_cita(estudio_id: str, fecha_hora: datetime):
    """Enviar confirmación de cita por email y SMS"""
    try:
        db = get_database()

        # Obtener información del estudio y paciente
        estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if not estudio:
            return

        paciente = await db.pacientes.find_one(
            {"_id": ObjectId(estudio["paciente_id"])}
        )
        if not paciente:
            return

        # Enviar email de confirmación
        await email_service.send_appointment_reminder(
            paciente["email"],
            paciente["nombre"],
            fecha_hora.strftime("%Y-%m-%d %H:%M"),
            estudio["tipo_estudio"],
        )

        # Enviar SMS de confirmación
        await sms_service.send_appointment_reminder(
            paciente["telefono"],
            paciente["nombre"],
            fecha_hora.strftime("%Y-%m-%d %H:%M"),
            estudio["tipo_estudio"],
        )

    except Exception as e:
        print(f"Error enviando confirmación de cita: {e}")
