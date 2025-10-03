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
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { FormsModule } from '@angular/forms';
import { EstudioFormComponent } from './forms/estudio-form';

export interface Estudio {
  id: string;
  paciente_id: string;
  paciente_nombre?: string;
  tipo_estudio: string;
  medico_solicitante: string;
  prioridad: string;
  indicaciones?: string;
  sala?: string;
  tecnico_asignado?: string;
  estado: string;
  fecha_solicitud: string;
  fecha_programada?: string;
  fecha_realizacion?: string;
  resultados?: string;
  created_at?: string;
  updated_at?: string;
  urgente?: boolean;
  modalidad?: string;
  parte_cuerpo?: string;
  contraste?: boolean;
  observaciones?: string;
  medico_referente?: string;
}

@Component({
  selector: 'app-estudios',
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
    MatDatepickerModule,
    MatNativeDateModule,
    FormsModule,
  ],
  templateUrl: './estudios.html',
  styleUrl: './estudios.scss',
})
export class Estudios implements OnInit {
  estudios: Estudio[] = [];
  filteredEstudios: Estudio[] = [];
  searchTerm: string = '';
  selectedEstado: string = 'Todos';
  selectedTipoEstudio: string = 'Todos';
  selectedModalidad: string = 'Todos';
  selectedUrgencia: string = 'Todos';
  selectedDate: Date | null = null;
  isLoading: boolean = true;
  expandedEstudioId: string | null = null;

  estadoOptions = [
    'Todos',
    'Pendiente',
    'Completado',
  ];

  tipoEstudioOptions = [
    'Todos',
    'Radiografía de Tórax',
    'Tomografía Abdominal',
    'Resonancia Magnética',
    'Ecografía',
    'Mamografía',
    'Densitometría Ósea',
  ];

  modalidadOptions = [
    'Todos',
    'RX',
    'CT',
    'MR',
    'US',
    'MG',
    'DX',
    'XA',
    'PT',
    'NM',
    'RF',
    'EC',
    'OT',
  ];

  urgenciaOptions = ['Todos', 'Urgente', 'Normal'];

  constructor(
    private api: Api,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadEstudios();
  }

  loadEstudios(): void {
    this.isLoading = true;
    const params = this.buildServerParams();
    this.api.get('api/estudios', params).subscribe({
      next: (response: any[]) => {
        this.estudios = response.map((e) => ({
          id: e.id,
          paciente_id: e.paciente_id,
          paciente_nombre: e.paciente_nombre || 'Paciente no encontrado',
          tipo_estudio: e.tipo_estudio,
          medico_solicitante: e.medico_solicitante,
          prioridad: e.prioridad,
          indicaciones: e.indicaciones,
          sala: e.sala,
          tecnico_asignado: e.tecnico_asignado,
          estado: this.formatEstadoForDisplay(e.estado),
          fecha_solicitud: e.fecha_solicitud,
          fecha_programada: e.fecha_programada,
          fecha_realizacion: e.fecha_realizacion,
          resultados: e.resultados,
          created_at: e.fecha_creacion,
          updated_at: e.fecha_actualizacion,
          urgente: (e.prioridad || '').toLowerCase() === 'urgente' || (e.prioridad || '').toLowerCase() === 'alta',
          modalidad: 'RX',
          parte_cuerpo: 'General',
          contraste: e.indicaciones?.toLowerCase().includes('contraste') || false,
          observaciones: e.indicaciones || e.resultados,
          medico_referente: e.medico_solicitante,
        }));
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudios:', error);
        this.estudios = [];
        this.isLoading = false;
      },
    });
  }

  private buildServerParams(): any {
    const params: any = {};
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      const estadoMap: Record<string, string> = {
        'Pendiente': 'pendiente',
        'Completado': 'completado',
      };
      params.estado = estadoMap[this.selectedEstado] || this.selectedEstado.toLowerCase();
    }
    if (this.selectedTipoEstudio && this.selectedTipoEstudio !== 'Todos') {
      params.tipo_estudio = this.selectedTipoEstudio;
    }
    if (this.selectedUrgencia && this.selectedUrgencia !== 'Todos') {
      params.prioridad = this.selectedUrgencia.toLowerCase();
    }
    return params;
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(EstudioFormComponent, {
      width: '700px',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadEstudios();
        this.showMessage('Estudio agregado exitosamente', 'success');
      }
    });
  }

  openEditDialog(estudio: Estudio): void {
    const dialogRef = this.dialog.open(EstudioFormComponent, {
      width: '700px',
      data: estudio,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadEstudios();
        this.showMessage('Estudio actualizado exitosamente', 'success');
      }
    });
  }

  deleteEstudio(estudio: Estudio): void {
    if (confirm(`¿Está seguro que desea eliminar el estudio de ${estudio.paciente_nombre}?`)) {
      this.api.delete(`api/estudios/${estudio.id}`).subscribe({
        next: (response) => {
          console.log('Estudio eliminado exitosamente:', response);
          this.loadEstudios();
          this.showMessage('Estudio eliminado exitosamente', 'success');
        },
        error: (error) => {
          console.error('Error al eliminar estudio:', error);
          this.showMessage(
            `Error al eliminar estudio: ${error.error?.detail || error.message}`,
            'error',
          );
        },
      });
    }
  }

  toggleExpand(estudioId: string): void {
    if (this.expandedEstudioId === estudioId) {
      this.expandedEstudioId = null;
    } else {
      this.expandedEstudioId = estudioId;
    }
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onEstadoChange(): void {
    this.loadEstudios();
  }

  onModalidadChange(): void {
    this.applyFilters();
  }

  onTipoEstudioChange(): void {
    this.loadEstudios();
  }

  onUrgenciaChange(): void {
    this.loadEstudios();
  }

  onDateChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    let filtered = [...this.estudios];

    // Filtro de búsqueda
    if (this.searchTerm && this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(
        (estudio) =>
          (estudio.paciente_nombre && estudio.paciente_nombre.toLowerCase().includes(term)) ||
          (estudio.tipo_estudio && estudio.tipo_estudio.toLowerCase().includes(term)) ||
          (estudio.medico_solicitante && estudio.medico_solicitante.toLowerCase().includes(term)) ||
          (estudio.parte_cuerpo && estudio.parte_cuerpo.toLowerCase().includes(term)) ||
          (estudio.observaciones && estudio.observaciones.toLowerCase().includes(term)),
      );
    }

    // Filtro de modalidad
    if (this.selectedModalidad && this.selectedModalidad !== 'Todos') {
      filtered = filtered.filter((estudio) => (estudio.modalidad || '') === this.selectedModalidad);
    }

    // Filtro de fecha - CORREGIDO
    if (this.selectedDate) {
      // Convertir la fecha seleccionada a formato YYYY-MM-DD
      const year = this.selectedDate.getFullYear();
      const month = String(this.selectedDate.getMonth() + 1).padStart(2, '0');
      const day = String(this.selectedDate.getDate()).padStart(2, '0');
      const selectedDateString = `${year}-${month}-${day}`;
      
      console.log('Fecha seleccionada:', selectedDateString);
      
      filtered = filtered.filter((estudio) => {
        if (!estudio.fecha_realizacion) {
          console.log('Estudio sin fecha:', estudio.id);
          return false;
        }
        
        // Extraer solo la parte de la fecha (YYYY-MM-DD) ignorando la hora
        const estudioDate = estudio.fecha_realizacion.split('T')[0];
        const matches = estudioDate === selectedDateString;
        
        console.log(`Comparando: ${estudioDate} === ${selectedDateString} = ${matches}`);
        
        return matches;
      });
      
      console.log('Estudios filtrados por fecha:', filtered.length);
    }

    this.filteredEstudios = filtered;
  }

  exportToCSV(): void {
    if (this.filteredEstudios.length === 0) {
      this.showMessage('No hay estudios para exportar', 'error');
      return;
    }

    // Definir las columnas del CSV
    const headers = [
      'ID',
      'Paciente',
      'Tipo de Estudio',
      'Estado',
      'Modalidad',
      'Parte del Cuerpo',
      'Fecha de Realización',
      'Médico Referente',
      'Urgente',
      'Contraste',
      'Observaciones'
    ];

    // Convertir datos a formato CSV
    const csvData = this.filteredEstudios.map(estudio => [
      estudio.id,
      estudio.paciente_nombre || '',
      estudio.tipo_estudio,
      estudio.estado,
      this.getModalidadName(estudio.modalidad),
      estudio.parte_cuerpo || '',
      estudio.fecha_realizacion ? new Date(estudio.fecha_realizacion).toLocaleDateString('es-ES') : '',
      estudio.medico_referente || '',
      estudio.urgente ? 'Sí' : 'No',
      estudio.contraste ? 'Sí' : 'No',
      estudio.observaciones || ''
    ]);

    // Crear el contenido del CSV
    let csvContent = headers.join(',') + '\n';
    csvData.forEach(row => {
      csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    // Crear y descargar el archivo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `estudios_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    this.showMessage(`${this.filteredEstudios.length} estudios exportados exitosamente`, 'success');
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case 'Pendiente':
        return 'estado-pendiente';
      case 'Completado':
        return 'estado-completado';
      default:
        return 'estado-default';
    }
  }

  formatEstadoForDisplay(estadoRaw: string): string {
    if (!estadoRaw) return '';
    const map: Record<string, string> = {
      pendiente: 'Pendiente',
      programado: 'Pendiente',
      en_proceso: 'Pendiente',
      completado: 'Completado',
      cancelado: 'Completado',
    };
    return map[estadoRaw] || estadoRaw;
  }

  getModalidadIcon(modalidad: string | undefined): string {
    if (!modalidad) return 'medical_services';
    switch (modalidad) {
      case 'RX':
        return 'photo_camera';
      case 'CT':
        return 'view_in_ar';
      case 'MR':
        return 'magnet';
      case 'US':
        return 'waves';
      case 'MG':
        return 'camera_alt';
      case 'DX':
        return 'image';
      case 'XA':
        return 'video_library';
      case 'PT':
        return 'radioactive';
      case 'NM':
        return 'radioactive';
      case 'RF':
        return 'healing';
      default:
        return 'medical_services';
    }
  }

  getModalidadName(modalidad: string | undefined): string {
    if (!modalidad) return 'No especificada';
    const modalidadNames: { [key: string]: string } = {
      RX: 'Radiografía',
      CT: 'Tomografía Computarizada',
      MR: 'Resonancia Magnética',
      US: 'Ultrasonido',
      MG: 'Mamografía',
      DX: 'Radiografía Digital',
      XA: 'Angiografía',
      PT: 'Tomografía por Emisión de Positrones',
      NM: 'Medicina Nuclear',
      RF: 'Radiología Fluoroscópica',
    };
    return modalidadNames[modalidad] || modalidad;
  }

  getEstudiosStats(): any {
    return {
      total: this.estudios.length,
      programados: this.estudios.filter((e) => e.estado === 'Pendiente').length,
      enProceso: 0,
      completados: this.estudios.filter((e) => e.estado === 'Completado').length,
      urgentes: this.estudios.filter((e) => e.urgente).length,
    };
  }

  getTodaysEstudios(): Estudio[] {
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    return this.estudios.filter(
      (estudio) => estudio.fecha_realizacion?.startsWith(todayString) || false,
    );
  }

  isToday(fecha: string | undefined): boolean {
    if (!fecha) return false;
    const fechaEstudio = new Date(fecha);
    const today = new Date();
    return fechaEstudio.toDateString() === today.toDateString();
  }

  isPending(estado: string): boolean {
    return estado === 'Pendiente';
  }
}