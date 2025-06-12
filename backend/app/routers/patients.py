from fastapi import APIRouter, HTTPException
from typing import List
from ..models.patient import Patient
from ..database import db
from bson import ObjectId

router = APIRouter(prefix="/patients", tags=["Pacientes"])

def patient_helper(patient) -> dict:
    patient["id"] = str(patient["_id"])
    del patient["_id"]
    return patient

@router.post("/", response_model=Patient)
async def create_patient(patient: Patient):
    result = await db.patients.insert_one(patient.dict(exclude={"id"}))
    patient.id = str(result.inserted_id)
    return patient

@router.get("/", response_model=List[Patient])
async def get_patients():
    patients = await db.patients.find().to_list(100)
    return [patient_helper(p) for p in patients]

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient_helper(patient)

@router.put("/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient: Patient):
    await db.patients.update_one({"_id": ObjectId(patient_id)}, {"$set": patient.dict(exclude={"id"})})
    return await get_patient(patient_id)

@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    result = await db.patients.delete_one({"_id": ObjectId(patient_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"message": "Paciente eliminado"}
