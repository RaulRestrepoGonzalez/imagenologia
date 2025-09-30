import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid
import numpy as np
from PIL import Image
import io
import logging
import shutil
from datetime import datetime
import uuid

from ..auth import get_current_user, UserRole, User
from ..database import db
from ..models import Estudio, Paciente

router = APIRouter(prefix="/api/dicom", tags=["dicom"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads/dicom"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def find_estudio_by_id(estudio_id: str):
    """Helper function to find a study by id or _id"""
    from bson import ObjectId
    
    # Try to find by id field
    estudio = await db.estudios.find_one({"id": estudio_id})
    if estudio:
        return estudio
    
    # Try to find by _id
    try:
        estudio = await db.estudios.find_one({"_id": ObjectId(estudio_id)})
        if estudio:
            return estudio
    except:
        pass
    
    return None

@router.get("/pacientes-con-estudios")
async def get_pacientes_con_estudios(
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Get list of all patients with their studies count
    """
    # Get all patients
    pacientes_db = await db.pacientes.find({}).to_list(length=None)
    
    # Get all studies
    estudios = await db.estudios.find({}).to_list(length=None)
    
    # Build patient list with study count
    pacientes = []
    for paciente in pacientes_db:
        # Count studies for this patient (using both id and _id for compatibility)
        paciente_id = paciente.get("id") or str(paciente.get("_id"))
        estudios_count = len([
            e for e in estudios 
            if e.get("paciente_id") == paciente_id or 
               e.get("paciente_id") == str(paciente.get("_id"))
        ])
        
        # Only include patients with at least one study
        if estudios_count > 0:
            pacientes.append({
                "id": paciente_id,
                "nombre": paciente.get("nombre"),
                "apellidos": paciente.get("apellidos", ""),
                "identificacion": paciente.get("identificacion"),
                "estudios_pendientes": estudios_count
            })
    
    # Sort by name
    pacientes.sort(key=lambda x: f"{x['nombre']} {x['apellidos']}")
    
    return pacientes

@router.get("/estudios-por-paciente/{paciente_id}")
async def get_estudios_por_paciente(
    paciente_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Get all studies for a specific patient
    """
    from bson import ObjectId
    
    # Verify patient exists (try both id and _id)
    paciente = await db.pacientes.find_one({"id": paciente_id})
    if not paciente:
        # Try with _id
        try:
            paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        except:
            pass
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Get ALL studies for this patient (not just pending)
    estudios = await db.estudios.find({
        "paciente_id": paciente_id
    }).to_list(length=None)
    
    # Format studies with patient info
    estudios_formateados = []
    for estudio in estudios:
        # Usar _id si no existe id
        estudio_id = estudio.get("id") or str(estudio.get("_id"))
        estudios_formateados.append({
            "id": estudio_id,
            "tipo_estudio": estudio.get("tipo_estudio"),
            "estado": estudio.get("estado"),
            "fecha_solicitud": estudio.get("fecha_solicitud"),
            "fecha_programada": estudio.get("fecha_programada"),
            "prioridad": estudio.get("prioridad", "normal"),
            "indicaciones": estudio.get("indicaciones"),
            "paciente_id": paciente_id,
            "paciente_nombre": paciente.get("nombre"),
            "paciente_apellidos": paciente.get("apellidos", ""),
            "paciente_cedula": paciente.get("identificacion")
        })
    
    return {
        "paciente": {
            "id": paciente_id,
            "nombre": paciente.get("nombre"),
            "apellidos": paciente.get("apellidos", ""),
            "identificacion": paciente.get("identificacion")
        },
        "estudios": estudios_formateados
    }

def convert_dicom_to_png(dicom_path: str, output_path: str):
    """Convert DICOM file to PNG format"""
    try:
        # Read DICOM file
        ds = pydicom.dcmread(dicom_path)
        
        # Convert to numpy array
        img_array = ds.pixel_array
        
        # Normalize to 0-255
        img_array = (img_array - np.min(img_array)) / (np.max(img_array) - np.min(img_array)) * 255.0
        img_array = img_array.astype(np.uint8)
        
        # Convert to PIL Image and save as PNG
        img = Image.fromarray(img_array)
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        logger.error(f"Error converting DICOM to PNG: {str(e)}")
        return False

@router.post("/upload/{estudio_id}")
async def upload_dicom_files(
    estudio_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Upload DICOM files for a specific study and automatically attach to patient's report
    """
    # Verify study exists and user has permission
    estudio = await find_estudio_by_id(estudio_id)
    if not estudio:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # Get patient information from study
    paciente_id = estudio.get("paciente_id")
    if not paciente_id:
        raise HTTPException(status_code=400, detail="Estudio no tiene paciente asignado")
    
    # Verify patient exists (try both id and _id)
    from bson import ObjectId
    paciente = await db.pacientes.find_one({"id": paciente_id})
    if not paciente:
        try:
            paciente = await db.pacientes.find_one({"_id": ObjectId(paciente_id)})
        except:
            pass
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    logger.info(f"Subiendo archivos DICOM para estudio {estudio_id} del paciente {paciente.get('nombre')} {paciente.get('apellidos', '')}")
    
    # Create study directory if it doesn't exist
    study_dir = os.path.join(UPLOAD_DIR, estudio_id)
    os.makedirs(study_dir, exist_ok=True)
    
    uploaded_files = []
    imagenes_para_informe = []
    
    for file in files:
        try:
            # Generate unique filename
            file_ext = ".dcm"
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(study_dir, filename)
            
            # Save DICOM file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Convert to PNG for preview
            png_filename = f"{os.path.splitext(filename)[0]}.png"
            png_path = os.path.join(study_dir, png_filename)
            
            if convert_dicom_to_png(file_path, png_path):
                file_info = {
                    "original_name": file.filename,
                    "saved_name": filename,
                    "preview_name": png_filename,
                    "size": os.path.getsize(file_path),
                    "uploaded_at": datetime.utcnow(),
                    "uploaded_by": current_user.email,
                    "paciente_id": paciente_id
                }
                uploaded_files.append(file_info)
                
                # Prepare image info for report
                imagenes_para_informe.append({
                    "archivo_dicom": filename,
                    "archivo_png": png_filename,
                    "estudio_id": estudio_id,
                    "descripcion": f"Imagen de {estudio.get('tipo_estudio', 'estudio')}",
                    "orden": len(imagenes_para_informe)
                })
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            continue
    
    # Update study with DICOM files
    if uploaded_files:
        from bson import ObjectId
        # Try to update by id or _id
        try:
            result = await db.estudios.update_one(
                {"id": estudio_id},
                {
                    "$push": {"archivos_dicom": {"$each": uploaded_files}},
                    "$set": {"estado": "completado", "fecha_actualizacion": datetime.utcnow()}
                }
            )
            if result.matched_count == 0:
                # Try with _id
                await db.estudios.update_one(
                    {"_id": ObjectId(estudio_id)},
                    {
                        "$push": {"archivos_dicom": {"$each": uploaded_files}},
                        "$set": {"estado": "completado", "fecha_actualizacion": datetime.utcnow()}
                    }
                )
        except:
            pass
        
        # Find or create report for this study and automatically attach images
        informe = await db.informes.find_one({"estudio_id": estudio_id})
        
        if informe:
            # Update existing report with new images
            from bson import ObjectId
            informe_id = informe.get("id") or str(informe.get("_id"))
            try:
                result = await db.informes.update_one(
                    {"id": informe_id},
                    {
                        "$push": {"imagenes_dicom": {"$each": imagenes_para_informe}},
                        "$set": {"fecha_actualizacion": datetime.utcnow()}
                    }
                )
                if result.matched_count == 0:
                    # Try with _id
                    await db.informes.update_one(
                        {"_id": informe["_id"]},
                        {
                            "$push": {"imagenes_dicom": {"$each": imagenes_para_informe}},
                            "$set": {"fecha_actualizacion": datetime.utcnow()}
                        }
                    )
            except:
                pass
            logger.info(f"Imágenes anexadas automáticamente al informe {informe_id}")
        else:
            # Create a draft report with the images
            nuevo_informe_id = str(uuid.uuid4())
            nuevo_informe = {
                "id": nuevo_informe_id,
                "estudio_id": estudio_id,
                "paciente_id": paciente_id,
                "medico_radiologo": current_user.email if current_user.role == UserRole.RADIOLOGO else "Por asignar",
                "fecha_informe": datetime.utcnow().isoformat(),
                "hallazgos": "Pendiente de análisis",
                "impresion_diagnostica": "Pendiente de análisis",
                "estado": "Borrador",
                "imagenes_dicom": imagenes_para_informe,
                "fecha_creacion": datetime.utcnow(),
                "fecha_actualizacion": datetime.utcnow(),
                "firmado": False,
                "urgente": False,
                "validado": False,
                # Patient info
                "paciente_nombre": paciente.get("nombre"),
                "paciente_apellidos": paciente.get("apellidos"),
                "paciente_cedula": paciente.get("identificacion"),
                # Study info
                "estudio_tipo": estudio.get("tipo_estudio"),
                "estudio_fecha": estudio.get("fecha_solicitud")
            }
            await db.informes.insert_one(nuevo_informe)
            logger.info(f"Informe borrador creado automáticamente con ID {nuevo_informe_id} e imágenes anexadas")
    
    return {
        "message": f"{len(uploaded_files)} archivos DICOM subidos exitosamente para el paciente {paciente.get('nombre')} {paciente.get('apellidos', '')}",
        "files": uploaded_files,
        "paciente": {
            "id": paciente_id,
            "nombre": paciente.get("nombre"),
            "apellidos": paciente.get("apellidos"),
            "identificacion": paciente.get("identificacion")
        },
        "imagenes_anexadas_a_informe": len(imagenes_para_informe)
    }

@router.get("/study/{estudio_id}")
async def get_dicom_files(
    estudio_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO, UserRole.PACIENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Get list of DICOM files for a study
    """
    # Verify study exists and user has permission
    estudio = await find_estudio_by_id(estudio_id)
    if not estudio:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # If user is a patient, verify they have access to this study
    if current_user.role == UserRole.PACIENTE and estudio.get("paciente_id") != current_user.paciente_id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")
    
    # Get DICOM files
    archivos_dicom = estudio.get("archivos_dicom", [])
    return {"estudio_id": estudio_id, "archivos": archivos_dicom}

@router.get("/preview/{estudio_id}/{filename}")
async def get_dicom_preview(
    estudio_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO, UserRole.PACIENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Get a preview image for a DICOM file
    """
    # Verify study exists and user has permission
    estudio = await find_estudio_by_id(estudio_id)
    if not estudio:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # If user is a patient, verify they have access to this study
    if current_user.role == UserRole.PACIENTE and estudio.get("paciente_id") != current_user.paciente_id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")
    
    # Check if file exists
    file_path = os.path.join(UPLOAD_DIR, estudio_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(file_path, media_type="image/png")

@router.get("/download/{estudio_id}/{filename}")
async def download_dicom_file(
    estudio_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario tiene uno de los roles permitidos
    if current_user.role not in [UserRole.ADMIN, UserRole.TECNICO, UserRole.RADIOLOGO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para acceder a este recurso"
        )
    """
    Download a DICOM file
    """
    # Verify study exists and user has permission
    estudio = await find_estudio_by_id(estudio_id)
    if not estudio:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    
    # Check if file exists
    file_path = os.path.join(UPLOAD_DIR, estudio_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        file_path,
        media_type="application/dicom",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
