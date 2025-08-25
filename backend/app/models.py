from datetime import datetime
from typing import Optional, List
from enum import Enum
from bson import ObjectId

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

class Paciente:
    def __init__(self, 
                 nombre: str, 
                 identificacion: str, 
                 email: str, 
                 telefono: str,
                 fecha_nacimiento: datetime,
                 direccion: Optional[str] = None,
                 genero: Optional[str] = None,
                 grupo_sanguineo: Optional[str] = None,
                 alergias: Optional[str] = None,
                 condiciones_cronicas: Optional[str] = None,
                 medicamentos: Optional[str] = None):
        self._id = ObjectId()
        self.nombre = nombre
        self.identificacion = identificacion
        self.email = email
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.genero = genero
        self.grupo_sanguineo = grupo_sanguineo
        self.alergias = alergias
        self.condiciones_cronicas = condiciones_cronicas
        self.medicamentos = medicamentos
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()

class Estudio:
    def __init__(self,
                 paciente_id: str,
                 tipo_estudio: str,
                 medico_solicitante: str,
                 prioridad: str = "normal",
                 indicaciones: Optional[str] = None,
                 sala: Optional[str] = None,
                 tecnico_asignado: Optional[str] = None):
        self._id = ObjectId()
        self.paciente_id = paciente_id
        self.tipo_estudio = tipo_estudio
        self.medico_solicitante = medico_solicitante
        self.prioridad = prioridad
        self.indicaciones = indicaciones
        self.sala = sala
        self.tecnico_asignado = tecnico_asignado
        self.estado = EstadoEstudio.PENDIENTE
        self.fecha_solicitud = datetime.now()
        self.fecha_programada: Optional[datetime] = None
        self.fecha_realizacion: Optional[datetime] = None
        self.resultados: Optional[str] = None
        self.archivos_dicom: List[str] = []
        self.fecha_actualizacion = datetime.now()

class Cita:
    def __init__(self,
                 estudio_id: str,
                 fecha_hora: datetime,
                 tecnico_asignado: str,
                 sala: str,
                 duracion_minutos: int = 30,
                 observaciones: Optional[str] = None):
        self._id = ObjectId()
        self.estudio_id = estudio_id
        self.fecha_hora = fecha_hora
        self.tecnico_asignado = tecnico_asignado
        self.sala = sala
        self.duracion_minutos = duracion_minutos
        self.estado = EstadoCita.PROGRAMADA
        self.asistio: Optional[bool] = None
        self.observaciones = observaciones
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()

class Informe:
    def __init__(self,
                 estudio_id: str,
                 medico_radiologo: str,
                 hallazgos: str,
                 conclusion: str,
                 recomendaciones: Optional[str] = None,
                 prioridad: str = "normal"):
        self._id = ObjectId()
        self.estudio_id = estudio_id
        self.medico_radiologo = medico_radiologo
        self.hallazgos = hallazgos
        self.conclusion = conclusion
        self.recomendaciones = recomendaciones
        self.prioridad = prioridad
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()
        self.firmado = False
        self.fecha_firma: Optional[datetime] = None

class Notificacion:
    def __init__(self,
                 paciente_id: str,
                 tipo: TipoNotificacion,
                 mensaje: str,
                 estudio_id: Optional[str] = None,
                 titulo: Optional[str] = None,
                 prioridad: str = "normal"):
        self._id = ObjectId()
        self.paciente_id = paciente_id
        self.estudio_id = estudio_id
        self.tipo = tipo
        self.titulo = titulo
        self.mensaje = mensaje
        self.prioridad = prioridad
        self.enviada = False
        self.fecha_creacion = datetime.now()
        self.fecha_envio: Optional[datetime] = None
        self.intentos_envio = 0
        self.ultimo_intento: Optional[datetime] = None