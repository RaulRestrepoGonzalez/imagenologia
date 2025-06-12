from fastapi import APIRouter, HTTPException
from typing import List
from ..models.appointment import Appointment
from ..database import db
from bson import ObjectId

router = APIRouter(prefix="/appointments", tags=["Citas"])

def appointment_helper(a) -> dict:
    a["id"] = str(a["_id"])
    del a["_id"]
    return a

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: Appointment):
    result = await db.appointments.insert_one(appointment.dict(exclude={"id"}))
    appointment.id = str(result.inserted_id)
    return appointment

@router.get("/", response_model=List[Appointment])
async def get_appointments():
    appointments = await db.appointments.find().to_list(100)
    return [appointment_helper(a) for a in appointments]
