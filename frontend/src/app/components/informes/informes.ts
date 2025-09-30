import { Component, OnInit } from '@angular/core';
import { Api } from '../../services/api';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatBadgeModule } from '@angular/material/badge';
import { MatExpansionModule } from '@angular/material/expansion';
import { FormsModule } from '@angular/forms';
import { InformeFormComponent } from './forms/informe-form';

export interface Informe {
  id: number;
  estudio_id: number;
  paciente_id: number;
  paciente_nombre: string;
  paciente_apellidos?: string;
  paciente_cedula?: string;
  estudio_tipo: string;
  estudio_modalidad?: string;
  estudio_fecha?: string;
  medico_radiologo: string;
  fecha_informe: string;
  hallazgos: string;
  impresion_diagnostica: string;
  recomendaciones: string;
  estado: string;
  tecnica_utilizada: string;
  calidad_estudio: string;
  urgente: boolean;
  validado: boolean;
  observaciones_tecnicas: string;
  imagenes_dicom?: any[]; // Imágenes DICOM convertidas a PNG
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-informes',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatDialogModule,
    MatIconModule,
    MatSnackBarModule,
    MatCardModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatChipsModule,
    MatBadgeModule,
    MatExpansionModule,
    FormsModule,
  ],
  templateUrl: './informes.html',
  styleUrl: './informes.scss',
})
export class Informes implements OnInit {
  informes: Informe[] = [];
  filteredInformes: Informe[] = [];
  searchTerm: string = '';
  selectedEstado: string = 'Todos';
  // Eliminados filtros de calidad y urgencia
  selectedValidacion: string = 'Todos';
  isLoading: boolean = true;
  environment = environment; // Para acceder a la URL del API

  estadoOptions = [
    'Todos',
    'Borrador',
    'En Revisión',
    'Completado',
    'Validado',
    'Entregado',
    'Corregido',
  ];

  // Eliminados: calidadOptions y urgenciaOptions

  validacionOptions = ['Todos', 'Validado', 'Pendiente'];

  constructor(
    private api: Api,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadInformes();
  }

  loadInformes(): void {
    this.isLoading = true;
    this.api.get('api/informes').subscribe({
      next: (response: any[]) => {
        console.log('Informes cargados desde el backend:', response);
        // Cargar informes con información completa del paciente y estudio
        this.informes = [];

        // Para cada informe, obtener información del estudio asociado
        const informesPromises = response.map(async (i) => {
          try {
            // Obtener datos del estudio
            const estudioResponse = await this.api.get(`api/estudios/${i.estudio_id}`).toPromise();

            return {
              id: i.id,
              estudio_id: i.estudio_id,
              paciente_id: estudioResponse?.paciente_id || i.paciente_id || 0,
              paciente_nombre:
                estudioResponse?.paciente_nombre || i.paciente_nombre || 'Desconocido',
              paciente_apellidos: estudioResponse?.paciente_apellidos || '',
              paciente_cedula: estudioResponse?.paciente_cedula || '',
              estudio_tipo: estudioResponse?.tipo_estudio || i.estudio_tipo || 'No especificado',
              estudio_modalidad: estudioResponse?.modalidad || 'No especificada',
              estudio_fecha: estudioResponse?.fecha_realizacion || '',
              medico_radiologo: i.medico_radiologo,
              fecha_informe: i.fecha_informe,
              hallazgos: i.hallazgos,
              impresion_diagnostica: i.impresion_diagnostica,
              recomendaciones: i.recomendaciones,
              estado: i.estado,
              tecnica_utilizada: i.tecnica_utilizada,
              calidad_estudio: i.calidad_estudio,
              urgente: i.urgente,
              validado: i.validado,
              observaciones_tecnicas: i.observaciones_tecnicas,
              created_at: i.fecha_creacion,
              updated_at: i.fecha_actualizacion,
            };
          } catch (error) {
            console.warn(`Error al cargar estudio ${i.estudio_id}:`, error);
            return {
              id: i.id,
              estudio_id: i.estudio_id,
              paciente_id: i.paciente_id || 0,
              paciente_nombre: i.paciente_nombre || 'Desconocido',
              paciente_apellidos: '',
              paciente_cedula: '',
              estudio_tipo: i.estudio_tipo || 'No especificado',
              estudio_modalidad: 'No especificada',
              estudio_fecha: '',
              medico_radiologo: i.medico_radiologo,
              fecha_informe: i.fecha_informe,
              hallazgos: i.hallazgos,
              impresion_diagnostica: i.impresion_diagnostica,
              recomendaciones: i.recomendaciones,
              estado: i.estado,
              tecnica_utilizada: i.tecnica_utilizada,
              calidad_estudio: i.calidad_estudio,
              urgente: i.urgente,
              validado: i.validado,
              observaciones_tecnicas: i.observaciones_tecnicas,
              created_at: i.fecha_creacion,
              updated_at: i.fecha_actualizacion,
            };
          }
        });

        Promise.all(informesPromises).then((informesCompletos) => {
          this.informes = informesCompletos;
          this.applyFilters();
          this.isLoading = false;
        });
      },
      error: (error) => {
        console.error('Error al cargar informes:', error);
        // Fallback a datos de ejemplo si hay error de conexión
        this.informes = [
          {
            id: 1,
            estudio_id: 1,
            paciente_id: 1,
            paciente_nombre: 'Juan Pérez',
            paciente_apellidos: 'García',
            paciente_cedula: '12345678',
            estudio_tipo: 'Radiografía de Tórax',
            estudio_modalidad: 'RX',
            estudio_fecha: '2024-01-15',
            medico_radiologo: 'Dr. Rodríguez',
            fecha_informe: '2024-01-15',
            hallazgos: 'Pulmones con campos pulmonares libres.',
            impresion_diagnostica: 'Radiografía de tórax normal',
            recomendaciones: 'Control en 6 meses',
            estado: 'Validado',
            tecnica_utilizada: 'Radiografía PA y lateral',
            calidad_estudio: 'Buena',
            urgente: false,
            validado: true,
            observaciones_tecnicas: 'Estudio satisfactorio',
          },
        ];
        this.applyFilters();
        this.isLoading = false;
      },
    });
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(InformeFormComponent, {
      width: '800px',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadInformes();
        this.showMessage('Informe creado exitosamente', 'success');
      }
    });
  }

  openEditDialog(informe: Informe): void {
    const dialogRef = this.dialog.open(InformeFormComponent, {
      width: '800px',
      data: informe,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadInformes();
        this.showMessage('Informe actualizado exitosamente', 'success');
      }
    });
  }

  deleteInforme(informe: Informe): void {
    if (confirm(`¿Está seguro que desea eliminar el informe de ${informe.paciente_nombre}?`)) {
      this.api.delete(`api/informes/${informe.id}`).subscribe({
        next: (response) => {
          console.log('Informe eliminado exitosamente:', response);
          this.loadInformes(); // Recargar la lista
          this.showMessage('Informe eliminado exitosamente', 'success');
        },
        error: (error) => {
          console.error('Error al eliminar informe:', error);
          this.showMessage(
            `Error al eliminar informe: ${error.error?.detail || error.message}`,
            'error',
          );
        },
      });
    }
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onEstadoChange(): void {
    this.applyFilters();
  }

  onCalidadChange(): void {
    this.applyFilters();
  }

  onUrgenciaChange(): void {
    this.applyFilters();
  }

  onValidacionChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    let filtered = [...this.informes];

    // Filtro por término de búsqueda
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(
        (informe) =>
          informe.paciente_nombre.toLowerCase().includes(term) ||
          (informe.paciente_apellidos && informe.paciente_apellidos.toLowerCase().includes(term)) ||
          (informe.paciente_cedula && informe.paciente_cedula.toLowerCase().includes(term)) ||
          informe.estudio_tipo.toLowerCase().includes(term) ||
          informe.medico_radiologo.toLowerCase().includes(term) ||
          informe.hallazgos.toLowerCase().includes(term),
      );
    }

    // Filtro por estado
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      filtered = filtered.filter((informe) => informe.estado === this.selectedEstado);
    }

    // Filtros de calidad y urgencia removidos

    // Filtro por validación
    if (this.selectedValidacion && this.selectedValidacion !== 'Todos') {
      const isValidado = this.selectedValidacion === 'Validado';
      filtered = filtered.filter((informe) => informe.validado === isValidado);
    }

    this.filteredInformes = filtered;
  }

  private showMessage(message: string, type: 'success' | 'error' | 'warning'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  syncImagenes(informe: Informe): void {
    if (!informe?.id) return;
    this.api.post(`api/informes/${informe.id}/sync-imagenes`, {}).subscribe({
      next: (resp: any) => {
        const n = resp?.sincronizadas ?? 0;
        this.showMessage(`Imágenes sincronizadas: ${n}`, n > 0 ? 'success' : 'warning');
        this.loadInformes();
      },
      error: (err) => {
        console.error('Error sincronizando imágenes:', err);
        this.showMessage('Error al sincronizar imágenes', 'error');
      },
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case 'Borrador':
        return 'estado-borrador';
      case 'En Revisión':
        return 'estado-en-revision';
      case 'Completado':
        return 'estado-completado';
      case 'Validado':
        return 'estado-validado';
      case 'Entregado':
        return 'estado-entregado';
      case 'Corregido':
        return 'estado-corregido';
      default:
        return 'estado-default';
    }
  }

  getCalidadClass(calidad: string): string {
    switch (calidad) {
      case 'Excelente':
        return 'calidad-excelente';
      case 'Buena':
        return 'calidad-buena';
      case 'Regular':
        return 'calidad-regular';
      case 'Deficiente':
        return 'calidad-deficiente';
      default:
        return 'calidad-default';
    }
  }

  formatFecha(fecha: string): string {
    return new Date(fecha).toLocaleDateString('es-ES');
  }

  getInformesCountByEstado(estado: string): number {
    return this.informes.filter((i) => i.estado === estado).length;
  }

  getInformesUrgentes(): number {
    return this.informes.filter((i) => i.urgente).length;
  }

  getInformesValidados(): number {
    return this.informes.filter((i) => i.validado).length;
  }

  getInformesPendientes(): number {
    return this.informes.filter((i) => !i.validado).length;
  }

  // Métodos faltantes para el template
  getInformesStats(): any {
    return {
      total: this.informes.length,
      borradores: this.getInformesCountByEstado('Borrador'),
      enRevision: this.getInformesCountByEstado('En Revisión'),
      validados: this.getInformesValidados(),
      urgentes: this.getInformesUrgentes(),
    };
  }

  getPendingReports(): Informe[] {
    return this.informes.filter((i) => !i.validado);
  }

  getUrgentReports(): Informe[] {
    return this.informes.filter((i) => i.urgente);
  }

  sortInformesByDate(): void {
    this.filteredInformes.sort(
      (a, b) => new Date(b.fecha_informe).getTime() - new Date(a.fecha_informe).getTime(),
    );
  }

  isPending(estado: string): boolean {
    return ['Borrador', 'En Revisión'].includes(estado);
  }

  isToday(fecha: string): boolean {
    const fechaInforme = new Date(fecha);
    const today = new Date();
    return fechaInforme.toDateString() === today.toDateString();
  }

  exportReport(informe: Informe): void {
    const win = window.open('', '_blank');
    if (!win) {
      this.showMessage('No se pudo abrir la ventana de exportación', 'error');
      return;
    }

    const html = `
      <html>
        <head>
          <title>Informe - ${informe.paciente_nombre}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #333; }
            h1 { margin: 0 0 8px 0; }
            h2 { margin: 0 0 16px 0; font-size: 16px; color: #555; }
            .section { margin: 16px 0; page-break-inside: avoid; }
            .title { font-weight: bold; text-transform: uppercase; font-size: 13px; margin-bottom: 8px; }
            .box { background: #f7f7f7; padding: 12px; border-radius: 6px; }
            .meta { font-size: 12px; color: #666; }
            .logos { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
            @media print { body { margin: 16mm; } }
          </style>
        </head>
        <body>
          <div class="logos">
            <div>
              <h1>INFORME MÉDICO</h1>
              <h2>${informe.estudio_tipo}</h2>
            </div>
          </div>

          <div class="section">
            <div class="title">Información del paciente</div>
            <div class="box">
              <div><strong>Nombre:</strong> ${informe.paciente_nombre} ${informe.paciente_apellidos || ''}</div>
              <div><strong>Cédula:</strong> ${informe.paciente_cedula || 'N/A'}</div>
              <div class="meta"><strong>Fecha del informe:</strong> ${this.formatFecha(informe.fecha_informe)}</div>
            </div>
          </div>

          <div class="section">
            <div class="title">Hallazgos</div>
            <div class="box">${(informe.hallazgos || '').replace(/\n/g, '<br>')}</div>
          </div>

          <div class="section">
            <div class="title">Impresión diagnóstica</div>
            <div class="box">${(informe.impresion_diagnostica || '').replace(/\n/g, '<br>')}</div>
          </div>

          <div class="section">
            <div class="title">Recomendaciones</div>
            <div class="box">${(informe.recomendaciones || 'Ninguna').replace(/\n/g, '<br>')}</div>
          </div>
        </body>
      </html>`;

    win.document.write(html);
    win.document.close();
    setTimeout(() => {
      win.print();
      win.close();
      this.showMessage('Exportación a PDF iniciada', 'success');
    }, 300);
  }

  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  async printReport(informe: Informe): Promise<void> {
    // Cargar imágenes como base64 primero
    const imagenesBase64: string[] = [];

    if (informe.imagenes_dicom && informe.imagenes_dicom.length > 0) {
      this.showMessage('Cargando imágenes...', 'success');

      for (const imagen of informe.imagenes_dicom) {
        try {
          // Determinar nombre de archivo PNG con fallbacks
          const pngFilename = imagen.archivo_png || imagen.preview_name || (imagen.archivo_dicom ? imagen.archivo_dicom.replace(/\.dcm$/i, '.png') : undefined);
          if (!pngFilename) {
            console.warn('No se encontró archivo PNG para la imagen:', imagen);
            imagenesBase64.push('');
            continue;
          }

          // Usar endpoint público sin auth
          const imageUrl = `${this.environment.apiUrl}/api/dicom/public/preview/${informe.estudio_id}/${encodeURIComponent(pngFilename)}`;
          console.log('Cargando imagen desde URL:', imageUrl);

          const response = await fetch(imageUrl);

          if (response.ok) {
            const blob = await response.blob();
            const base64 = await this.blobToBase64(blob);
            imagenesBase64.push(base64);
            console.log(`Imagen cargada exitosamente: ${pngFilename}`);
          } else {
            // Intentar directamente endpoint base64
            try {
              const b64Url = `${this.environment.apiUrl}/api/dicom/public/base64/${informe.estudio_id}/${encodeURIComponent(pngFilename)}`;
              const b64Resp = await fetch(b64Url);
              if (b64Resp.ok) {
                const data = await b64Resp.json();
                if (data?.data) {
                  imagenesBase64.push(data.data);
                  continue;
                }
              }
            } catch (e) {
              console.warn('Fallo en endpoint base64 directo:', e);
            }
            // Reintentar si existe preview_name distinto
            if (imagen.preview_name && imagen.preview_name !== pngFilename) {
              try {
                const altUrl = `${this.environment.apiUrl}/api/dicom/public/preview/${informe.estudio_id}/${encodeURIComponent(imagen.preview_name)}`;
                console.log('Reintentando con preview_name:', altUrl);
                const altResp = await fetch(altUrl);
                if (altResp.ok) {
                  const blob = await altResp.blob();
                  const base64 = await this.blobToBase64(blob);
                  imagenesBase64.push(base64);
                  continue;
                }
              } catch (e) {
                console.error('Fallo en reintento con preview_name:', e);
              }
            }

            // Fallback final: consultar lista pública y usar el primer PNG disponible
            try {
              const listUrl = `${this.environment.apiUrl}/api/dicom/public/list/${informe.estudio_id}`;
              const listResp = await fetch(listUrl);
              if (listResp.ok) {
                const listData = await listResp.json();
                const firstPng: string | undefined = listData?.png_files?.[0];
                if (firstPng) {
                  const firstUrl = `${this.environment.apiUrl}/api/dicom/public/preview/${informe.estudio_id}/${encodeURIComponent(firstPng)}`;
                  const firstResp = await fetch(firstUrl);
                  if (firstResp.ok) {
                    const blob = await firstResp.blob();
                    const base64 = await this.blobToBase64(blob);
                    imagenesBase64.push(base64);
                    continue;
                  }
                }
              }
            } catch (e) {
              console.warn('Fallo en fallback de lista pública:', e);
            }
            console.error(
              `Error cargando imagen ${pngFilename}: ${response.status} - ${response.statusText}`,
            );
            // Intentar obtener más detalles del error
            try {
              const errorText = await response.text();
              console.error('Detalles del error:', errorText);
            } catch (e) {
              console.error('No se pudo obtener detalles del error');
            }
            imagenesBase64.push(''); // Imagen vacía si falla
          }
        } catch (error) {
          console.error('Error cargando imagen:', error);
          imagenesBase64.push(''); // Imagen vacía si falla
        }
      }
    }

    const printWindow = window.open('', '_blank');
    if (printWindow) {
      // Generar HTML de imágenes DICOM
      let imagenesHTML = '';
      const imagenesValidas = imagenesBase64.filter((img) => img && img.length > 0);

      if (
        informe.imagenes_dicom &&
        informe.imagenes_dicom.length > 0 &&
        imagenesValidas.length > 0
      ) {
        imagenesHTML = `
          <div class="section page-break">
            <div class="section-title">IMÁGENES DEL ESTUDIO</div>
            <div class="images-grid">
        `;

        informe.imagenes_dicom.forEach((imagen: any, index: number) => {
          // Solo incluir imágenes que se cargaron exitosamente
          if (imagenesBase64[index] && imagenesBase64[index].length > 0) {
            imagenesHTML += `
              <div class="image-container">
                <img src="${imagenesBase64[index]}" alt="Imagen ${index + 1}" class="dicom-image" />
                <p class="image-caption">Imagen ${index + 1}: ${imagen.descripcion || `Imagen DICOM - ${imagen.archivo_png || 'Sin nombre'}`}</p>
              </div>
            `;
          }
        });

        imagenesHTML += `
            </div>
          </div>
        `;
      } else if (
        informe.imagenes_dicom &&
        informe.imagenes_dicom.length > 0 &&
        imagenesValidas.length === 0
      ) {
        // Si hay imágenes configuradas pero ninguna se pudo cargar
        imagenesHTML = `
          <div class="section">
            <div class="section-title">IMÁGENES DEL ESTUDIO</div>
            <p style="color: #666; font-style: italic;">
              Se detectaron ${informe.imagenes_dicom.length} imagen(es) asociada(s) al estudio,
              pero no se pudieron cargar para la impresión. Verifique la configuración del sistema.
            </p>
          </div>
        `;
      }

      printWindow.document.write(`
        <html>
          <head>
            <title>Informe - ${informe.paciente_nombre}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
              }
              .header {
                text-align: center;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
              }
              .section {
                margin: 20px 0;
                page-break-inside: avoid;
              }
              .section-title {
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
                font-size: 16px;
                text-transform: uppercase;
              }
              .patient-info {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
              }
              .images-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 15px;
              }
              .image-container {
                text-align: center;
                page-break-inside: avoid;
                margin-bottom: 20px;
              }
              .dicom-image {
                max-width: 100%;
                max-height: 400px;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                object-fit: contain;
              }
              .image-caption {
                margin-top: 8px;
                font-size: 12px;
                color: #666;
                font-style: italic;
              }
              .page-break {
                page-break-before: always;
              }
              @media print {
                body { margin: 15px; }
                .section { page-break-inside: avoid; }
                .image-container { page-break-inside: avoid; }
              }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>INFORME MÉDICO</h1>
              <h2>${informe.estudio_tipo}</h2>
            </div>

            <div class="section">
              <div class="section-title">INFORMACIÓN DEL PACIENTE</div>
              <div class="patient-info">
                <strong>Nombre:</strong> ${informe.paciente_nombre} ${informe.paciente_apellidos || ''}<br>
                <strong>Cédula:</strong> ${informe.paciente_cedula || 'N/A'}<br>
                <strong>Médico Radiólogo:</strong> ${informe.medico_radiologo}<br>
                <strong>Fecha del Informe:</strong> ${this.formatFecha(informe.fecha_informe)}
              </div>
            </div>

            <div class="section">
              <div class="section-title">HALLAZGOS</div>
              <p>${informe.hallazgos}</p>
            </div>

            <div class="section">
              <div class="section-title">IMPRESIÓN DIAGNÓSTICA</div>
              <p>${informe.impresion_diagnostica}</p>
            </div>

            <div class="section">
              <div class="section-title">RECOMENDACIONES</div>
              <p>${informe.recomendaciones || 'Ninguna recomendación específica.'}</p>
            </div>

            <div class="section">
              <div class="section-title">TÉCNICA UTILIZADA</div>
              <p>${informe.tecnica_utilizada || 'No especificada'}</p>
            </div>

            <div class="section">
              <div class="section-title">CALIDAD DEL ESTUDIO</div>
              <p>${informe.calidad_estudio}</p>
            </div>

            ${imagenesHTML}
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }

    const totalImagenes = informe.imagenes_dicom ? informe.imagenes_dicom.length : 0;
    const imagenesCargadas = imagenesBase64.filter((img) => img && img.length > 0).length;

    if (totalImagenes > 0) {
      if (imagenesCargadas === totalImagenes) {
        this.showMessage(
          `Informe enviado a impresión con ${imagenesCargadas} imagen(es)`,
          'success',
        );
      } else {
        this.showMessage(
          `Informe enviado a impresión. ${imagenesCargadas} de ${totalImagenes} imágenes cargadas`,
          'warning',
        );
      }
    } else {
      this.showMessage('Informe enviado a impresión', 'success');
    }
  }
}
