from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    RADIOLOGO = "radiologo"
    SECRETARIO = "secretario"
    PACIENTE = "paciente"

class EstadoEstudio(str, Enum):
    PENDIENTE = "pendiente"
    PROGRAMADO = "programado"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class EstadoCita(str, Enum):
    PROGRAMADA = "programada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    NO_ASISTIO = "no_asistio"

class TipoNotificacion(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class PacienteBase(BaseModel):
    nombre: str
    apellidos: Optional[str] = None
    identificacion: str
    email: EmailStr
    telefono: str
    fecha_nacimiento: datetime
    direccion: Optional[str] = None
    genero: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    alergias: Optional[str] = None
    condiciones_cronicas: Optional[str] = None
    medicamentos: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class EstudioBase(BaseModel):
    paciente_id: str
    tipo_estudio: str
    medico_solicitante: str
    prioridad: str = "normal"
    indicaciones: Optional[str] = None
    sala: Optional[str] = None
    tecnico_asignado: Optional[str] = None

class EstudioCreate(EstudioBase):
    pass

class Estudio(EstudioBase):
    id: str
    estado: EstadoEstudio
    fecha_solicitud: datetime
    fecha_programada: Optional[datetime] = None
    fecha_realizacion: Optional[datetime] = None
    resultados: Optional[str] = None
    archivos_dicom: List[str] = []
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class CitaBase(BaseModel):
    paciente_id: str
    fecha_cita: datetime
    tipo_estudio: str
    observaciones: Optional[str] = None
    estado: EstadoCita = EstadoCita.PROGRAMADA

class CitaCreate(CitaBase):
    estudio_id: Optional[str] = None
    tecnico_asignado: Optional[str] = None
    sala: Optional[str] = None
    duracion_minutos: int = 30

class Cita(CitaBase):
    id: str
    estudio_id: Optional[str] = None
    tecnico_asignado: Optional[str] = None
    sala: Optional[str] = None
    duracion_minutos: int = 30
    asistio: Optional[bool] = None
    paciente_nombre: Optional[str] = None
    paciente_apellidos: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class InformeBase(BaseModel):
    estudio_id: str
    medico_radiologo: str
    hallazgos: str
    conclusion: str
    recomendaciones: Optional[str] = None
    prioridad: str = "normal"

class InformeCreate(InformeBase):
    pass

class Informe(InformeBase):
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    firmado: bool
    fecha_firma: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificacionBase(BaseModel):
    paciente_id: str
    tipo: TipoNotificacion
    mensaje: str
    estudio_id: Optional[str] = None
    titulo: Optional[str] = None
    prioridad: str = "normal"

class NotificacionCreate(NotificacionBase):
    pass

class Notificacion(NotificacionBase):
    id: str
    enviada: bool
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None
    intentos_envio: int
    ultimo_intento: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas adicionales para operaciones específicas
class EstudioUpdate(BaseModel):
    estado: Optional[EstadoEstudio] = None
    resultados: Optional[str] = None
    sala: Optional[str] = None
    tecnico_asignado: Optional[str] = None
    indicaciones: Optional[str] = None

class CitaUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    tecnico_asignado: Optional[str] = None
    sala: Optional[str] = None
    duracion_minutos: Optional[int] = None
    estado: Optional[EstadoCita] = None
    observaciones: Optional[str] = None
    asistio: Optional[bool] = None

class PacienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    genero: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    alergias: Optional[str] = None
    condiciones_cronicas: Optional[str] = None
    medicamentos: Optional[str] = None

# User Authentication Schemas
class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: Optional[str] = None
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    paciente_id: Optional[str] = None  # Link to patient record if role is PACIENTE

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    paciente_id: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None