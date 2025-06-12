from pydantic import BaseModel
from typing import Optional
from datetime import date

class Patient(BaseModel):
    id: Optional[str]
    full_name: str
    document: str
    birth_date: date
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]

