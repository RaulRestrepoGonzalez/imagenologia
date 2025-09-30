# Solución para Imágenes DICOM en Impresión de Informes

## Descripción del Problema

Las imágenes DICOM convertidas a PNG no aparecen al momento de imprimir el informe médico. El sistema convierte correctamente los archivos DICOM a PNG pero hay problemas en el flujo de carga e impresión.

## Diagnóstico Realizado

### 1. Análisis del Flujo Actual

**Backend (Python/FastAPI):**
- ✅ Conversión DICOM → PNG funciona correctamente
- ✅ Almacenamiento en `uploads/dicom/{estudio_id}/`
- ✅ Endpoint `/api/dicom/preview/{estudio_id}/{filename}` disponible
- ✅ Datos guardados en campo `imagenes_dicom` del informe

**Frontend (Angular):**
- ❌ Error en el nombre del campo para archivo PNG
- ❌ Manejo deficiente de errores de carga
- ❌ URLs mal construidas en algunos casos

### 2. Problemas Identificados

1. **Campo incorrecto en frontend:** Usaba `imagen.preview_name` en lugar de `imagen.archivo_png`
2. **Manejo de errores insuficiente:** No había logging detallado para debuggear
3. **Validación de datos:** Faltaba verificar que el campo `archivo_png` existiera
4. **Feedback al usuario:** No informaba sobre el estado de carga de imágenes

## Soluciones Implementadas

### 1. Corrección del Frontend (`informes.ts`)

**Cambios realizados:**

```typescript
// ANTES (incorrecto)
const imageUrl = `${this.environment.apiUrl}/api/dicom/preview/${informe.estudio_id}/${imagen.archivo_png || imagen.preview_name}`;

// DESPUÉS (correcto)
const pngFilename = imagen.archivo_png;
if (!pngFilename) {
  console.warn('No se encontró archivo PNG para la imagen:', imagen);
  imagenesBase64.push('');
  continue;
}
const imageUrl = `${this.environment.apiUrl}/api/dicom/preview/${informe.estudio_id}/${pngFilename}`;
```

**Mejoras añadidas:**
- ✅ Validación de existencia del campo `archivo_png`
- ✅ Logging detallado para debugging
- ✅ Mejor manejo de errores HTTP
- ✅ Feedback mejorado al usuario
- ✅ Filtrado de imágenes válidas antes de mostrar
- ✅ Mensaje informativo cuando hay imágenes pero no se pueden cargar

### 2. Mejora del Backend (`dicom.py`)

**Cambios realizados:**

```python
# Logging detallado para debugging
logger.info(f"Solicitando preview de imagen: estudio_id={estudio_id}, filename={filename}")

# Mejor manejo de errores
if not os.path.exists(file_path):
    logger.error(f"Archivo no encontrado en ruta: {file_path}")
    # Listar archivos disponibles para debugging
    study_dir = os.path.join(UPLOAD_DIR, estudio_id)
    if os.path.exists(study_dir):
        available_files = os.listdir(study_dir)
        logger.info(f"Archivos disponibles: {available_files}")
```

### 3. Endpoint de Debug (`informes.py`)

**Nuevo endpoint añadido:**

```python
@router.get("/informes/{informe_id}/debug/imagenes")
async def debug_imagenes_informe(informe_id: str):
    """Debug endpoint para verificar el estado de las imágenes DICOM"""
```

Este endpoint permite verificar:
- ✅ Si el informe tiene imágenes configuradas
- ✅ Si los archivos PNG existen físicamente
- ✅ Si los archivos DICOM originales existen
- ✅ Qué archivos están disponibles en el directorio

## Cómo Verificar la Solución

### 1. Script de Prueba Automatizado

Ejecutar el script de prueba incluido:

```bash
cd imagenologia
python test_print_images.py
```

Este script:
- ✅ Verifica conexión a la base de datos
- ✅ Busca informes con imágenes DICOM
- ✅ Verifica existencia de archivos PNG
- ✅ Simula el proceso de impresión
- ✅ Genera reporte detallado

### 2. Verificación Manual via API

**Paso 1: Listar informes con imágenes**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/informes
```

**Paso 2: Debug de un informe específico**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/informes/{INFORME_ID}/debug/imagenes
```

**Paso 3: Probar carga de imagen**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/dicom/preview/{ESTUDIO_ID}/{FILENAME}.png
```

### 3. Verificación desde el Frontend

1. Abrir DevTools → Console
2. Ir a la sección de Informes
3. Hacer clic en "Imprimir" en un informe con imágenes
4. Verificar en la consola:
   - ✅ "Cargando imágenes..."
   - ✅ "Cargando imagen desde URL: ..."
   - ✅ "Imagen cargada exitosamente: ..."
   - ✅ "Informe enviado a impresión con X imagen(es)"

## Estructura de Datos Correcta

### Documento de Informe en MongoDB

```json
{
  "_id": "ObjectId",
  "estudio_id": "string",
  "paciente_id": "string",
  "medico_radiologo": "string",
  "hallazgos": "string",
  "impresion_diagnostica": "string",
  "imagenes_dicom": [
    {
      "archivo_dicom": "uuid.dcm",
      "archivo_png": "uuid.png",
      "estudio_id": "string",
      "descripcion": "Imagen de Radiografía",
      "orden": 0
    }
  ]
}
```

### Estructura de Archivos en Servidor

```
uploads/dicom/
├── {estudio_id_1}/
│   ├── uuid1.dcm
│   ├── uuid1.png  ← Archivo PNG convertido
│   ├── uuid2.dcm
│   └── uuid2.png
├── {estudio_id_2}/
│   ├── uuid3.dcm
│   └── uuid3.png
```

## Troubleshooting

### Problema: "No se encontró archivo PNG"

**Posibles causas:**
1. El campo `archivo_png` está vacío o null
2. El archivo PNG no se generó correctamente durante la subida
3. El archivo fue eliminado del servidor

**Solución:**
```bash
# Verificar estructura de datos
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/informes/{ID}/debug/imagenes

# Re-convertir archivos DICOM si es necesario
# (Implementar endpoint de re-conversión si se requiere)
```

### Problema: "Error 403 - Permisos insuficientes"

**Causa:** El usuario no tiene rol adecuado para acceder a las imágenes

**Solución:**
- Verificar que el usuario tenga rol: ADMIN, TECNICO, RADIOLOGO, o PACIENTE
- Para pacientes, verificar que `estudio.paciente_id == user.paciente_id`

### Problema: "Error 404 - Estudio no encontrado"

**Causa:** El `estudio_id` en el informe no coincide con ningún estudio

**Solución:**
```bash
# Verificar integridad de datos
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/estudios/{ESTUDIO_ID}
```

### Problema: "Imágenes se cargan pero no aparecen en impresión"

**Posibles causas:**
1. Error en conversión a Base64
2. Imágenes muy grandes
3. Error en el HTML de impresión

**Solución:**
- Verificar logs del navegador durante impresión
- Revisar tamaño de archivos PNG
- Probar con imágenes más pequeñas

## Mantenimiento Preventivo

### 1. Monitoreo Regular

**Script de verificación semanal:**
```bash
#!/bin/bash
# Ejecutar cada semana para verificar integridad
cd /path/to/imagenologia
python test_print_images.py > /var/log/dicom_health_check.log 2>&1
```

### 2. Limpieza de Archivos Huérfanos

**Identificar archivos sin referencia en BD:**
```python
# Script para encontrar archivos PNG sin referencia en informes
# (Implementar según necesidades)
```

### 3. Backup de Imágenes

**Respaldar directorio de uploads:**
```bash
# Backup diario del directorio de imágenes
tar -czf backup_dicom_$(date +%Y%m%d).tar.gz uploads/dicom/
```

## Testing Continuo

### Tests Automatizados

1. **Test de conversión DICOM → PNG**
2. **Test de carga de imágenes en impresión**
3. **Test de integridad de datos**
4. **Test de permisos de acceso**

### Métricas de Monitoreo

- ✅ Tasa de éxito de impresión con imágenes
- ✅ Tiempo promedio de carga de imágenes
- ✅ Errores 404 en endpoints de preview
- ✅ Espacio usado en directorio uploads

## Contacto y Soporte

Para problemas adicionales:
1. Revisar logs del backend: `backend.log`
2. Revisar logs del frontend: DevTools → Console
3. Ejecutar script de diagnóstico: `python test_print_images.py`
4. Usar endpoint de debug: `/api/informes/{id}/debug/imagenes`

---

**Última actualización:** $(date)
**Estado:** ✅ SOLUCIONADO
**Versión:** 1.0