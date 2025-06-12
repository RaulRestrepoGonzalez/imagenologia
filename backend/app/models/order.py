from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Order(BaseModel):
    id: Optional[str]
    patient_id: str
    description: str
    status: str = "pendiente"
    created_at: datetime = datetime.utcnow()
