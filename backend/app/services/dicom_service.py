import os
import shutil
from datetime import datetime
from fastapi import HTTPException, UploadFile
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import generate_uid
import numpy as np
from PIL import Image
import io
import base64
from app.database import get_database
from bson import ObjectId
import json

class DICOMService:
    def __init__(self):
        self.upload_dir = "uploads/dicom"
        self.processed_dir = "processed/dicom"
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    async def process_dicom_file(self, file: UploadFile, estudio_id: str, paciente_id: str):
        try:
            # Guardar archivo subido
            file_path = os.path.join(self.upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Leer metadata DICOM
            dataset = pydicom.dcmread(file_path)
            
            # Extraer metadata relevante
            metadata = {
                "patient_name": str(dataset.PatientName) if hasattr(dataset, 'PatientName') else "",
                "patient_id": str(dataset.PatientID) if hasattr(dataset, 'PatientID') else "",
                "study_date": str(dataset.StudyDate) if hasattr(dataset, 'StudyDate') else "",
                "modality": str(dataset.Modality) if hasattr(dataset, 'Modality') else "",
                "study_description": str(dataset.StudyDescription) if hasattr(dataset, 'StudyDescription') else "",
                "series_description": str(dataset.SeriesDescription) if hasattr(dataset, 'SeriesDescription') else "",
                "rows": int(dataset.Rows) if hasattr(dataset, 'Rows') else 0,
                "columns": int(dataset.Columns) if hasattr(dataset, 'Columns') else 0,
                "bits_allocated": int(dataset.BitsAllocated) if hasattr(dataset, 'BitsAllocated') else 0,
                "bits_stored": int(dataset.BitsStored) if hasattr(dataset, 'BitsStored') else 0,
            }
            
            # Generar vista previa (thumbnail)
            preview_path = await self.generate_preview(dataset, estudio_id)
            
            # Guardar información en la base de datos
            db = get_database()
            
            dicom_data = {
                "estudio_id": estudio_id,
                "paciente_id": paciente_id,
                "original_filename": file.filename,
                "file_path": file_path,
                "preview_path": preview_path,
                "metadata": metadata,
                "fecha_subida": datetime.now(),
                "procesado": True
            }
            
            result = await db.dicom_files.insert_one(dicom_data)
            
            # Actualizar el estudio para incluir referencia al archivo DICOM
            await db.estudios.update_one(
                {"_id": ObjectId(estudio_id)},
                {"$push": {"archivos_dicom": str(result.inserted_id)}}
            )
            
            return {
                "id": str(result.inserted_id),
                "filename": file.filename,
                "metadata": metadata,
                "preview_url": f"/api/dicom/preview/{str(result.inserted_id)}"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando archivo DICOM: {str(e)}")
    
    async def generate_preview(self, dataset, estudio_id: str):
        try:
            # Crear una imagen a partir de los datos de píxeles DICOM
            if hasattr(dataset, 'pixel_array'):
                pixel_array = dataset.pixel_array
                
                # Normalizar los valores de píxeles para que estén en el rango 0-255
                if pixel_array.dtype != np.uint8:
                    pixel_array = ((pixel_array - pixel_array.min()) / 
                                 (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
                
                # Crear imagen PIL
                if len(pixel_array.shape) == 2:  # 2D array (una sola imagen)
                    image = Image.fromarray(pixel_array)
                else:  # 3D array (múltiples frames), tomar el primero
                    image = Image.fromarray(pixel_array[0])
                
                # Redimensionar para vista previa
                image.thumbnail((256, 256))
                
                # Guardar vista previa
                preview_filename = f"preview_{estudio_id}.png"
                preview_path = os.path.join(self.processed_dir, preview_filename)
                image.save(preview_path, "PNG")
                
                return preview_path
            else:
                # Si no hay datos de píxeles, crear una imagen en blanco
                preview_filename = f"preview_{estudio_id}.png"
                preview_path = os.path.join(self.processed_dir, preview_filename)
                
                # Crear una imagen en blanco
                image = Image.new('L', (256, 256), color=0)
                image.save(preview_path, "PNG")
                
                return preview_path
                
        except Exception as e:
            # En caso de error, aún así crear una imagen en blanco
            preview_filename = f"preview_{estudio_id}.png"
            preview_path = os.path.join(self.processed_dir, preview_filename)
            
            image = Image.new('L', (256, 256), color=0)
            image.save(preview_path, "PNG")
            
            return preview_path
    
    async def get_dicom_metadata(self, dicom_id: str):
        db = get_database()
        dicom_file = await db.dicom_files.find_one({"_id": ObjectId(dicom_id)})
        
        if not dicom_file:
            raise HTTPException(status_code=404, detail="Archivo DICOM no encontrado")
        
        return dicom_file["metadata"]
    
    async def get_dicom_preview(self, dicom_id: str):
        db = get_database()
        dicom_file = await db.dicom_files.find_one({"_id": ObjectId(dicom_id)})
        
        if not dicom_file:
            raise HTTPException(status_code=404, detail="Archivo DICOM no encontrado")
        
        preview_path = dicom_file.get("preview_path")
        
        if not preview_path or not os.path.exists(preview_path):
            # Generar una imagen por defecto si no hay vista previa
            default_image = Image.new('L', (256, 256), color=0)
            img_byte_arr = io.BytesIO()
            default_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return img_byte_arr
        
        with open(preview_path, "rb") as f:
            return f.read()
    
    async def get_dicom_file(self, dicom_id: str):
        db = get_database()
        dicom_file = await db.dicom_files.find_one({"_id": ObjectId(dicom_id)})
        
        if not dicom_file:
            raise HTTPException(status_code=404, detail="Archivo DICOM no encontrado")
        
        file_path = dicom_file.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo DICOM no encontrado en el sistema de archivos")
        
        return file_path
    
    async def get_estudio_dicom_files(self, estudio_id: str):
        db = get_database()
        dicom_files = []
        
        async for dicom_file in db.dicom_files.find({"estudio_id": estudio_id}):
            dicom_files.append({
                "id": str(dicom_file["_id"]),
                "filename": dicom_file["original_filename"],
                "upload_date": dicom_file["fecha_subida"],
                "metadata": dicom_file["metadata"]
            })
        
        return dicom_files
    
    async def delete_dicom_file(self, dicom_id: str):
        db = get_database()
        
        # Obtener información del archivo
        dicom_file = await db.dicom_files.find_one({"_id": ObjectId(dicom_id)})
        
        if not dicom_file:
            raise HTTPException(status_code=404, detail="Archivo DICOM no encontrado")
        
        # Eliminar archivos del sistema de archivos
        if dicom_file.get("file_path") and os.path.exists(dicom_file["file_path"]):
            os.remove(dicom_file["file_path"])
        
        if dicom_file.get("preview_path") and os.path.exists(dicom_file["preview_path"]):
            os.remove(dicom_file["preview_path"])
        
        # Eliminar referencia del estudio
        await db.estudios.update_one(
            {"_id": ObjectId(dicom_file["estudio_id"])},
            {"$pull": {"archivos_dicom": dicom_id}}
        )
        
        # Eliminar registro de la base de datos
        result = await db.dicom_files.delete_one({"_id": ObjectId(dicom_id)})
        
        if result.deleted_count == 1:
            return {"message": "Archivo DICOM eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error eliminando archivo DICOM")
    
    async def generate_dicom_from_image(self, image_data, paciente_info, estudio_info):
        """
        Crear un archivo DICOM a partir de una imagen y metadata
        """
        try:
            # Crear metadata básica del archivo DICOM
            file_meta = FileMetaDataset()
            file_meta.MediaStorageSOPClassUID = generate_uid()
            file_meta.MediaStorageSOPInstanceUID = generate_uid()
            file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            
            # Crear dataset DICOM
            dataset = FileDataset(
                f"{estudio_info['tipo_estudio']}_{paciente_info['identificacion']}",
                {},
                file_meta=file_meta,
                preamble=b"\0" * 128
            )
            
            # Agregar metadata del paciente
            dataset.PatientName = paciente_info['nombre']
            dataset.PatientID = paciente_info['identificacion']
            
            # Agregar metadata del estudio
            dataset.StudyDate = datetime.now().strftime("%Y%m%d")
            dataset.StudyTime = datetime.now().strftime("%H%M%S")
            dataset.Modality = "OT"  # Otro (por defecto)
            dataset.StudyDescription = estudio_info['tipo_estudio']
            
            # Configurar parámetros de la imagen
            dataset.Rows = image_data.shape[0]
            dataset.Columns = image_data.shape[1]
            dataset.BitsAllocated = 8
            dataset.BitsStored = 8
            dataset.HighBit = 7
            dataset.PixelRepresentation = 0
            
            if len(image_data.shape) == 3:
                dataset.SamplesPerPixel = image_data.shape[2]
                if image_data.shape[2] == 3:
                    dataset.PhotometricInterpretation = "RGB"
                else:
                    dataset.PhotometricInterpretation = "MONOCHROME2"
            else:
                dataset.SamplesPerPixel = 1
                dataset.PhotometricInterpretation = "MONOCHROME2"
            
            # Agregar datos de píxeles
            dataset.PixelData = image_data.tobytes()
            
            # Guardar archivo DICOM
            filename = f"{paciente_info['identificacion']}_{estudio_info['tipo_estudio']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dcm"
            file_path = os.path.join(self.upload_dir, filename)
            dataset.save_as(file_path)
            
            return file_path
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando archivo DICOM: {str(e)}")
        



