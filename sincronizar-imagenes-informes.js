// Script para sincronizar imágenes DICOM de estudios a informes
// Ejecutar con: mongosh imagenologia sincronizar-imagenes-informes.js

print("🔄 Sincronizando imágenes DICOM de estudios a informes...\n");

// Obtener todos los informes
const informes = db.informes.find({}).toArray();
let actualizados = 0;
let sinCambios = 0;

informes.forEach(informe => {
    // Buscar el estudio correspondiente
    const estudio = db.estudios.findOne({ 
        $or: [
            { _id: ObjectId(informe.estudio_id) },
            { id: informe.estudio_id }
        ]
    });
    
    if (!estudio) {
        print(`⚠️  Informe ${informe._id}: Estudio ${informe.estudio_id} no encontrado`);
        return;
    }
    
    // Verificar si el estudio tiene archivos DICOM
    if (!estudio.archivos_dicom || estudio.archivos_dicom.length === 0) {
        print(`ℹ️  Informe ${informe._id}: Estudio sin archivos DICOM`);
        sinCambios++;
        return;
    }
    
    // Verificar si el informe ya tiene las imágenes
    if (informe.imagenes_dicom && informe.imagenes_dicom.length > 0) {
        print(`✅ Informe ${informe._id}: Ya tiene ${informe.imagenes_dicom.length} imágenes`);
        sinCambios++;
        return;
    }
    
    // Convertir archivos DICOM a formato de imágenes para el informe
    const imagenes = estudio.archivos_dicom.map((archivo, index) => ({
        archivo_dicom: archivo.saved_name || archivo.original_name,
        archivo_png: archivo.preview_name || archivo.saved_name.replace('.dcm', '.png'),
        estudio_id: informe.estudio_id,
        descripcion: `Imagen ${index + 1} - ${archivo.original_name}`,
        orden: index
    }));
    
    // Actualizar el informe
    const resultado = db.informes.updateOne(
        { _id: informe._id },
        { 
            $set: { 
                imagenes_dicom: imagenes,
                fecha_actualizacion: new Date()
            } 
        }
    );
    
    if (resultado.modifiedCount > 0) {
        print(`✅ Informe ${informe._id}: Agregadas ${imagenes.length} imágenes`);
        actualizados++;
    }
});

print(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
print(`📊 RESUMEN:`);
print(`   ✅ Informes actualizados: ${actualizados}`);
print(`   ℹ️  Informes sin cambios: ${sinCambios}`);
print(`   📝 Total de informes: ${informes.length}`);
print(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
