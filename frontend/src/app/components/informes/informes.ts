import { Component, OnInit } from '@angular/core';
import { Api } from '../../services/api';
import { CommonModule } from '@angular/common';
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
  estudio_tipo: string;
  medico_radiologo: string;
  fecha_informe: string;
  hallazgos: string;
  impresion_diagnostica: string;
  recomendaciones?: string;
  estado: string;
  tecnica_utilizada?: string;
  calidad_estudio: string;
  urgente: boolean;
  validado: boolean;
  observaciones_tecnicas?: string;
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
  selectedCalidad: string = 'Todos';
  selectedUrgencia: string = 'Todos';
  selectedValidacion: string = 'Todos';
  isLoading: boolean = true;

  estadoOptions = [
    'Todos',
    'Borrador',
    'En Revisión',
    'Completado',
    'Validado',
    'Entregado',
    'Corregido',
  ];

  calidadOptions = ['Todos', 'Excelente', 'Buena', 'Regular', 'Deficiente'];

  urgenciaOptions = ['Todos', 'Urgente', 'Normal'];

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
    // Simular datos de ejemplo para demostración
    this.informes = [
      {
        id: 1,
        estudio_id: 1,
        paciente_id: 1,
        paciente_nombre: 'Juan Pérez',
        estudio_tipo: 'Radiografía de Tórax',
        medico_radiologo: 'Dr. Rodríguez',
        fecha_informe: '2024-01-15T10:30:00',
        hallazgos: 'Pulmones con campos pulmonares libres. Silueta cardíaca normal. No se observan masas ni derrames pleurales.',
        impresion_diagnostica: 'Radiografía de tórax normal',
        recomendaciones: 'Control en 6 meses si persisten síntomas',
        estado: 'Validado',
        tecnica_utilizada: 'Radiografía PA y lateral',
        calidad_estudio: 'Buena',
        urgente: false,
        validado: true,
        observaciones_tecnicas: 'Estudio técnicamente satisfactorio'
      },
      {
        id: 2,
        estudio_id: 2,
        paciente_id: 2,
        paciente_nombre: 'María García',
        estudio_tipo: 'Tomografía Abdominal',
        medico_radiologo: 'Dr. Martínez',
        fecha_informe: '2024-01-15T15:00:00',
        hallazgos: 'Hígado de tamaño normal. Vesícula biliar sin cálculos. Páncreas y riñones sin alteraciones.',
        impresion_diagnostica: 'Tomografía abdominal normal',
        recomendaciones: 'Seguimiento clínico',
        estado: 'En Revisión',
        tecnica_utilizada: 'TC helicoidal con contraste IV',
        calidad_estudio: 'Excelente',
        urgente: true,
        validado: false,
        observaciones_tecnicas: 'Estudio con contraste intravenoso'
      }
    ];
    this.applyFilters();
    this.isLoading = false;
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
      this.informes = this.informes.filter(i => i.id !== informe.id);
      this.applyFilters();
      this.showMessage('Informe eliminado exitosamente', 'success');
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
          informe.estudio_tipo.toLowerCase().includes(term) ||
          informe.medico_radiologo.toLowerCase().includes(term) ||
          informe.hallazgos.toLowerCase().includes(term),
      );
    }

    // Filtro por estado
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      filtered = filtered.filter((informe) => informe.estado === this.selectedEstado);
    }

    // Filtro por calidad
    if (this.selectedCalidad && this.selectedCalidad !== 'Todos') {
      filtered = filtered.filter((informe) => informe.calidad_estudio === this.selectedCalidad);
    }

    // Filtro por urgencia
    if (this.selectedUrgencia && this.selectedUrgencia !== 'Todos') {
      const isUrgente = this.selectedUrgencia === 'Urgente';
      filtered = filtered.filter((informe) => informe.urgente === isUrgente);
    }

    // Filtro por validación
    if (this.selectedValidacion && this.selectedValidacion !== 'Todos') {
      const isValidado = this.selectedValidacion === 'Validado';
      filtered = filtered.filter((informe) => informe.validado === isValidado);
    }

    this.filteredInformes = filtered;
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
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
    return this.informes.filter(i => i.estado === estado).length;
  }

  getInformesUrgentes(): number {
    return this.informes.filter(i => i.urgente).length;
  }

  getInformesValidados(): number {
    return this.informes.filter(i => i.validado).length;
  }

  getInformesPendientes(): number {
    return this.informes.filter(i => !i.validado).length;
  }

  // Métodos faltantes para el template
  getInformesStats(): any {
    return {
      total: this.informes.length,
      borradores: this.getInformesCountByEstado('Borrador'),
      enRevision: this.getInformesCountByEstado('En Revisión'),
      validados: this.getInformesValidados(),
      urgentes: this.getInformesUrgentes()
    };
  }

  getPendingReports(): Informe[] {
    return this.informes.filter(i => !i.validado);
  }

  getUrgentReports(): Informe[] {
    return this.informes.filter(i => i.urgente);
  }

  sortInformesByDate(): void {
    this.filteredInformes.sort((a, b) => 
      new Date(b.fecha_informe).getTime() - new Date(a.fecha_informe).getTime()
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
    // Simular exportación
    const content = `
      INFORME MÉDICO
      ===============
      Paciente: ${informe.paciente_nombre}
      Estudio: ${informe.estudio_tipo}
      Médico: ${informe.medico_radiologo}
      Fecha: ${this.formatFecha(informe.fecha_informe)}
      
      HALLAZGOS:
      ${informe.hallazgos}
      
      IMPRESIÓN DIAGNÓSTICA:
      ${informe.impresion_diagnostica}
      
      RECOMENDACIONES:
      ${informe.recomendaciones || 'Ninguna'}
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `informe_${informe.paciente_nombre}_${this.formatFecha(informe.fecha_informe)}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    this.showMessage('Informe exportado exitosamente', 'success');
  }

  printReport(informe: Informe): void {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Informe - ${informe.paciente_nombre}</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
              .section { margin: 20px 0; }
              .section-title { font-weight: bold; color: #333; margin-bottom: 10px; }
              .patient-info { background: #f5f5f5; padding: 15px; border-radius: 5px; }
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
                <strong>Nombre:</strong> ${informe.paciente_nombre}<br>
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
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
    
    this.showMessage('Informe enviado a impresión', 'success');
  }
}
