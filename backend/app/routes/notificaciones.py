from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas import NotificacionCreate, Notificacion
from app.database import get_database
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter()
email_service = EmailService()
sms_service = SMSService()

@router.post("/notificaciones", response_model=Notificacion)
async def create_notificacion(notificacion: NotificacionCreate, background_tasks: BackgroundTasks):
    """Crear una nueva notificación"""
    try:
        db = get_database()
        
        # Verificar que el paciente existe
        paciente = await db.pacientes.find_one({"_id": ObjectId(notificacion.paciente_id)})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Verificar que el estudio existe si se proporciona
        if notificacion.estudio_id:
            estudio = await db.estudios.find_one({"_id": ObjectId(notificacion.estudio_id)})
            if not estudio:
                raise HTTPException(status_code=404, detail="Estudio no encontrado")
        
        notificacion_dict = notificacion.dict()
        notificacion_dict["enviada"] = False
        notificacion_dict["fecha_creacion"] = datetime.now()
        notificacion_dict["intentos_envio"] = 0
        
        result = await db.notificaciones.insert_one(notificacion_dict)
        new_notificacion = await db.notificaciones.find_one({"_id": result.inserted_id})
        
        # Enviar notificación en segundo plano
        background_tasks.add_task(send_notification, str(new_notificacion["_id"]))
        
        new_notificacion["id"] = str(new_notificacion["_id"])
        return Notificacion(**new_notificacion)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente o estudio inválido")

async def send_notification(notificacion_id: str):
    """Enviar notificación en segundo plano"""
    try:
        db = get_database()
        notificacion = await db.notificaciones.find_one({"_id": ObjectId(notificacion_id)})
        
        if not notificacion:
            return
        
        paciente = await db.pacientes.find_one({"_id": ObjectId(notificacion["paciente_id"])})
        if not paciente:
            return
        
        success = False
        
        try:
            if notificacion["tipo"] == "email":
                success = await email_service.send_email(
                    paciente["email"],
                    notificacion.get("titulo", "Actualización de su estudio médico"),
                    notificacion["mensaje"]
                )
            elif notificacion["tipo"] == "sms":
                success = await sms_service.send_sms(
                    paciente["telefono"],
                    notificacion["mensaje"]
                )
            
            if success:
                # Marcar como enviada
                await db.notificaciones.update_one(
                    {"_id": ObjectId(notificacion_id)},
                    {"$set": {
                        "enviada": True,
                        "fecha_envio": datetime.now(),
                        "ultimo_intento": datetime.now()
                    }}
                )
            else:
                # Incrementar contador de intentos
                await db.notificaciones.update_one(
                    {"_id": ObjectId(notificacion_id)},
                    {"$inc": {"intentos_envio": 1}, "$set": {"ultimo_intento": datetime.now()}}
                )
                
        except Exception as e:
            # Incrementar contador de intentos en caso de error
            await db.notificaciones.update_one(
                {"_id": ObjectId(notificacion_id)},
                {"$inc": {"intentos_envio": 1}, "$set": {"ultimo_intento": datetime.now()}}
            )
            print(f"Error enviando notificación {notificacion_id}: {e}")
            
    except Exception as e:
        print(f"Error en send_notification: {e}")

@router.get("/notificaciones", response_model=List[Notificacion])
async def get_notificaciones(skip: int = 0, limit: int = 100, enviada: bool = None):
    """Obtener lista de notificaciones con filtros opcionales"""
    db = get_database()
    query = {}
    
    if enviada is not None:
        query["enviada"] = enviada
    
    notificaciones = []
    async for notificacion in db.notificaciones.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1):
        notificacion["id"] = str(notificacion["_id"])
        notificaciones.append(Notificacion(**notificacion))
    
    return notificaciones

@router.get("/notificaciones/{notificacion_id}", response_model=Notificacion)
async def get_notificacion(notificacion_id: str):
    """Obtener una notificación específica por ID"""
    try:
        db = get_database()
        notificacion = await db.notificaciones.find_one({"_id": ObjectId(notificacion_id)})
        
        if notificacion:
            notificacion["id"] = str(notificacion["_id"])
            return Notificacion(**notificacion)
        else:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de notificación inválido")

@router.get("/pacientes/{paciente_id}/notificaciones", response_model=List[Notificacion])
async def get_notificaciones_paciente(paciente_id: str, skip: int = 0, limit: int = 100):
    """Obtener todas las notificaciones de un paciente específico"""
    try:
        db = get_database()
        
        # Verificar que el paciente existe
        paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        notificaciones = []
        async for notificacion in db.notificaciones.find({"paciente_id": paciente_id}).skip(skip).limit(limit).sort("fecha_creacion", -1):
            notificacion["id"] = str(notificacion["_id"])
            notificaciones.append(Notificacion(**notificacion))
        
        return notificaciones
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

@router.post("/estudios/{estudio_id}/notificaciones/estado")
async def notificar_estado_estudio(estudio_id: str, background_tasks: BackgroundTasks):
    """Crear notificaciones automáticas cuando cambia el estado de un estudio"""
    try:
        db = get_database()
        estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        
        if not estudio:
            raise HTTPException(status_code=404, detail="Estudio no encontrado")
        
        paciente = await db.pacientes.find_one({"_id": ObjectId(estudio["paciente_id"])})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Crear mensaje según el estado
        if estudio["estado"] == "programado":
            mensaje = f"Su estudio de {estudio['tipo_estudio']} ha sido programado."
            titulo = "Estudio Programado"
        elif estudio["estado"] == "en_proceso":
            mensaje = f"Su estudio de {estudio['tipo_estudio']} está en proceso."
            titulo = "Estudio en Proceso"
        elif estudio["estado"] == "completado":
            mensaje = f"Su estudio de {estudio['tipo_estudio']} ha sido completado. Los resultados estarán disponibles pronto."
            titulo = "Estudio Completado"
        else:
            return {"message": "No se requiere notificación para este estado"}
        
        # Crear notificación por email
        notificacion_email = NotificacionCreate(
            paciente_id=str(paciente["_id"]),
            tipo="email",
            titulo=titulo,
            mensaje=mensaje,
            estudio_id=estudio_id,
            prioridad="normal"
        )
        
        # Crear notificación por SMS
        notificacion_sms = NotificacionCreate(
            paciente_id=str(paciente["_id"]),
            tipo="sms",
            mensaje=mensaje,
            estudio_id=estudio_id,
            prioridad="normal"
        )
        
        # Crear las notificaciones en segundo plano
        background_tasks.add_task(create_notificacion, notificacion_email, BackgroundTasks())
        background_tasks.add_task(create_notificacion, notificacion_sms, BackgroundTasks())
        
        return {"message": "Notificaciones programadas"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de estudio inválido")

@router.post("/notificaciones/{notificacion_id}/reenviar")
async def reenviar_notificacion(notificacion_id: str, background_tasks: BackgroundTasks):
    """Reenviar una notificación fallida"""
    try:
        db = get_database()
        
        # Verificar que la notificación existe
        notificacion = await db.notificaciones.find_one({"_id": ObjectId(notificacion_id)})
        if not notificacion:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        # Solo se pueden reenviar notificaciones no enviadas
        if notificacion["enviada"]:
            raise HTTPException(status_code=400, detail="La notificación ya fue enviada exitosamente")
        
        # Reenviar en segundo plano
        background_tasks.add_task(send_notification, notificacion_id)
        
        return {"message": "Notificación programada para reenvío"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de notificación inválido")

@router.delete("/notificaciones/{notificacion_id}")
async def delete_notificacion(notificacion_id: str):
    """Eliminar una notificación"""
    try:
        db = get_database()
        
        # Verificar que la notificación existe
        notificacion = await db.notificaciones.find_one({"_id": ObjectId(notificacion_id)})
        if not notificacion:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        result = await db.notificaciones.delete_one({"_id": ObjectId(notificacion_id)})
        
        if result.deleted_count == 1:
            return {"message": "Notificación eliminada correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar la notificación")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de notificación inválido")
