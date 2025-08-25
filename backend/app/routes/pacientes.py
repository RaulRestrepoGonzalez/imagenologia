from fastapi import APIRouter, HTTPException
from app.schemas import PacienteCreate, Paciente, PacienteUpdate
from app.database import get_database, object_id_to_str
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter()

@router.get("/pacientes", response_model=List[Paciente])
async def get_pacientes(skip: int = 0, limit: int = 100):
    """Obtener lista de pacientes con paginación"""
    db = get_database()
    pacientes = []
    
    async for paciente in db.pacientes.find().skip(skip).limit(limit):
        paciente["id"] = str(paciente["_id"])
        pacientes.append(Paciente(**paciente))
    
    return pacientes

@router.get("/pacientes/{paciente_id}", response_model=Paciente)
async def get_paciente(paciente_id: str):
    """Obtener un paciente específico por ID"""
    try:
        db = get_database()
        paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        
        if paciente:
            paciente["id"] = str(paciente["_id"])
            return Paciente(**paciente)
        else:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

@router.post("/pacientes", response_model=Paciente)
async def create_paciente(paciente: PacienteCreate):
    """Crear un nuevo paciente"""
    db = get_database()
    
    # Verificar que no exista un paciente con la misma identificación
    existing_patient = await db.pacientes.find_one({"identificacion": paciente.identificacion})
    if existing_patient:
        raise HTTPException(status_code=400, detail="Ya existe un paciente con esa identificación")
    
    # Verificar que no exista un paciente con el mismo email
    existing_email = await db.pacientes.find_one({"email": paciente.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Ya existe un paciente con ese email")
    
    paciente_dict = paciente.dict()
    paciente_dict["fecha_creacion"] = datetime.now()
    paciente_dict["fecha_actualizacion"] = datetime.now()
    
    result = await db.pacientes.insert_one(paciente_dict)
    new_paciente = await db.pacientes.find_one({"_id": result.inserted_id})
    
    new_paciente["id"] = str(new_paciente["_id"])
    return Paciente(**new_paciente)

@router.put("/pacientes/{paciente_id}", response_model=Paciente)
async def update_paciente(paciente_id: str, paciente: PacienteUpdate):
    """Actualizar un paciente existente"""
    try:
        db = get_database()
        
        # Verificar que el paciente existe
        existing_patient = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        if not existing_patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Preparar datos de actualización
        update_data = {}
        for field, value in paciente.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        update_data["fecha_actualizacion"] = datetime.now()
        
        # Verificar duplicados si se está actualizando identificación o email
        if "identificacion" in update_data:
            existing_id = await db.pacientes.find_one({
                "identificacion": update_data["identificacion"],
                "_id": {"$ne": ObjectId(paciente_id)}
            })
            if existing_id:
                raise HTTPException(status_code=400, detail="Ya existe un paciente con esa identificación")
        
        if "email" in update_data:
            existing_email = await db.pacientes.find_one({
                "email": update_data["email"],
                "_id": {"$ne": ObjectId(paciente_id)}
            })
            if existing_email:
                raise HTTPException(status_code=400, detail="Ya existe un paciente con ese email")
        
        result = await db.pacientes.update_one(
            {"_id": ObjectId(paciente_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            updated_paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
            updated_paciente["id"] = str(updated_paciente["_id"])
            return Paciente(**updated_paciente)
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar el paciente")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

@router.delete("/pacientes/{paciente_id}")
async def delete_paciente(paciente_id: str):
    """Eliminar un paciente (soft delete)"""
    try:
        db = get_database()
        
        # Verificar que el paciente existe
        existing_patient = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        if not existing_patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Verificar que no tenga estudios activos
        active_studies = await db.estudios.count_documents({
            "paciente_id": paciente_id,
            "estado": {"$in": ["pendiente", "programado", "en_proceso"]}
        })
        
        if active_studies > 0:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar el paciente porque tiene estudios activos"
            )
        
        # Soft delete: marcar como inactivo en lugar de eliminar
        result = await db.pacientes.update_one(
            {"_id": ObjectId(paciente_id)},
            {"$set": {
                "estado": "inactivo",
                "fecha_actualizacion": datetime.now()
            }}
        )
        
        if result.modified_count == 1:
            return {"message": "Paciente marcado como inactivo correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al marcar el paciente como inactivo")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

@router.get("/pacientes/{paciente_id}/estudios")
async def get_estudios_paciente(paciente_id: str):
    """Obtener todos los estudios de un paciente"""
    try:
        db = get_database()
        
        # Verificar que el paciente existe
        paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        estudios = []
        async for estudio in db.estudios.find({"paciente_id": paciente_id}).sort("fecha_solicitud", -1):
            estudio["id"] = str(estudio["_id"])
            estudios.append(estudio)
        
        return {"paciente": paciente, "estudios": estudios}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

