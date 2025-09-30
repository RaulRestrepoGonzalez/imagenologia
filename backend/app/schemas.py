from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    RADIOLOGO = "radiologo"
    SECRETARIO = "secretario"
    TECNICO = "tecnico"
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
    archivos_dicom: List[dict] = []  # Cambiado de List[str] a List[dict]
    fecha_actualizacion: datetime
    # Campos adicionales para información del paciente
    paciente_nombre: Optional[str] = None
    paciente_apellidos: Optional[str] = None
    paciente_cedula: Optional[str] = None
    paciente_edad: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class CitaBase(BaseModel):
    paciente_id: str
    fecha_cita: datetime
    tipo_estudio: str
    tipo_cita: str = "Consulta General"
    observaciones: Optional[str] = None
    estado: str = "programada"


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


class ImagenDICOM(BaseModel):
    """Información de una imagen DICOM anexada al informe"""

    archivo_dicom: str  # Nombre del archivo DICOM original
    archivo_png: str  # Nombre del archivo PNG convertido
    estudio_id: str  # ID del estudio al que pertenece
    descripcion: Optional[str] = None  # Descripción opcional de la imagen
    orden: int = 0  # Orden de visualización en el informe


class InformeBase(BaseModel):
    estudio_id: str
    medico_radiologo: str
    fecha_informe: str
    hallazgos: str
    impresion_diagnostica: str
    recomendaciones: Optional[str] = None
    estado: str = "Borrador"
    tecnica_utilizada: Optional[str] = None
    calidad_estudio: str = "Buena"
    urgente: bool = False
    validado: bool = False
    observaciones_tecnicas: Optional[str] = None
    imagenes_dicom: List[ImagenDICOM] = []  # Imágenes anexadas al informe


class InformeCreate(InformeBase):
    pass


class InformeUpdate(BaseModel):
    estudio_id: Optional[str] = None
    medico_radiologo: Optional[str] = None
    fecha_informe: Optional[str] = None
    hallazgos: Optional[str] = None
    impresion_diagnostica: Optional[str] = None
    recomendaciones: Optional[str] = None
    estado: Optional[str] = None
    tecnica_utilizada: Optional[str] = None
    calidad_estudio: Optional[str] = None
    urgente: Optional[bool] = None
    validado: Optional[bool] = None
    observaciones_tecnicas: Optional[str] = None


class Informe(InformeBase):
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    firmado: bool = False
    fecha_firma: Optional[datetime] = None
    # Campos adicionales para información del paciente y estudio
    paciente_id: Optional[str] = None
    paciente_nombre: Optional[str] = None
    paciente_apellidos: Optional[str] = None
    paciente_cedula: Optional[str] = None
    estudio_tipo: Optional[str] = None
    estudio_modalidad: Optional[str] = None
    estudio_fecha: Optional[datetime] = None

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
    fecha_cita: Optional[datetime] = None
    tipo_estudio: Optional[str] = None
    tipo_cita: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None
    tecnico_asignado: Optional[str] = None
    sala: Optional[str] = None
    duracion_minutos: Optional[int] = None
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
