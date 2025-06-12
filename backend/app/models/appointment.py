from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Appointment(BaseModel):
    id: Optional[str]
    patient_id: str
    date_time: datetime
    notes: Optional[str]
    