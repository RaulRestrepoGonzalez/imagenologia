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
  // Legacy fields for template compatibility
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
  isLoading: boolean = true;

  estadoOptions = [
    'Todos',
    'Programado',
    'En Proceso',
    'Completado',
    'Interpretado',
    'Informado',
    'Entregado',
    'Cancelado',
  ];

  tipoEstudioOptions = [
    'Todos',
    'Radiografía de Tórax',
    'Tomografía Abdominal',
    'Resonancia Magnética',
    'Ecografía',
    'Mamografía',
    'Densitometría Ósea'
  ];

  modalidadOptions = ['Todos', 'RX', 'CT', 'MR', 'US', 'MG', 'DX', 'XA', 'PT', 'NM', 'RF', 'EC', 'OT'];

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
    this.api.get('api/estudios').subscribe({
      next: (response: any[]) => {
        this.estudios = response.map(e => ({
          id: e.id,
          paciente_id: e.paciente_id,
          paciente_nombre: e.paciente_nombre || 'Paciente no encontrado',
          tipo_estudio: e.tipo_estudio,
          medico_solicitante: e.medico_solicitante,
          prioridad: e.prioridad,
          indicaciones: e.indicaciones,
          sala: e.sala,
          tecnico_asignado: e.tecnico_asignado,
          estado: e.estado,
          fecha_solicitud: e.fecha_solicitud,
          fecha_programada: e.fecha_programada,
          fecha_realizacion: e.fecha_realizacion,
          resultados: e.resultados,
          created_at: e.fecha_creacion,
          updated_at: e.fecha_actualizacion,
          // Map to legacy fields for template compatibility
          urgente: e.prioridad === 'urgente' || e.prioridad === 'alta',
          modalidad: 'RX', // Default modalidad
          parte_cuerpo: 'General', // Default parte_cuerpo
          contraste: e.indicaciones?.toLowerCase().includes('contraste') || false,
          observaciones: e.indicaciones || e.resultados,
          medico_referente: e.medico_solicitante
        }));
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudios:', error);
        this.estudios = [];
        this.isLoading = false;
      }
    });
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
      this.estudios = this.estudios.filter(e => e.id !== estudio.id);
      this.applyFilters();
      this.showMessage('Estudio eliminado exitosamente', 'success');
    }
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onEstadoChange(): void {
    this.applyFilters();
  }

  onModalidadChange(): void {
    this.applyFilters();
  }

  onTipoEstudioChange(): void {
    this.applyFilters();
  }

  onUrgenciaChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    console.log('Aplicando filtros estudios - Datos originales:', this.estudios.length);
    console.log('Filtros activos:', {
      searchTerm: this.searchTerm,
      selectedEstado: this.selectedEstado,
      selectedTipoEstudio: this.selectedTipoEstudio
    });
    
    let filtered = [...this.estudios];

    // Filtro por término de búsqueda
    if (this.searchTerm && this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(
        (estudio) =>
          (estudio.paciente_nombre && estudio.paciente_nombre.toLowerCase().includes(term)) ||
          (estudio.tipo_estudio && estudio.tipo_estudio.toLowerCase().includes(term)) ||
          (estudio.medico_solicitante && estudio.medico_solicitante.toLowerCase().includes(term))
      );
      console.log('Después de filtro de búsqueda estudios:', filtered.length);
    }

    // Filtro por estado
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      filtered = filtered.filter((estudio) => estudio.estado === this.selectedEstado);
      console.log('Después de filtro de estado estudios:', filtered.length);
    }

    // Filtro por tipo de estudio
    if (this.selectedTipoEstudio && this.selectedTipoEstudio !== 'Todos') {
      filtered = filtered.filter((estudio) => estudio.tipo_estudio === this.selectedTipoEstudio);
      console.log('Después de filtro de tipo estudio estudios:', filtered.length);
    }

    this.filteredEstudios = filtered;
    console.log('Resultado final filtrado estudios:', this.filteredEstudios.length);
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case 'Programado':
        return 'estado-programado';
      case 'En Proceso':
        return 'estado-en-proceso';
      case 'Completado':
        return 'estado-completado';
      case 'Interpretado':
        return 'estado-interpretado';
      case 'Informado':
        return 'estado-informado';
      case 'Entregado':
        return 'estado-entregado';
      case 'Cancelado':
        return 'estado-cancelado';
      default:
        return 'estado-default';
    }
  }

  getModalidadIcon(modalidad: string): string {
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

  formatFecha(fecha: string): string {
    return new Date(fecha).toLocaleDateString('es-ES');
  }

  getEstudiosCountByEstado(estado: string): number {
    return this.estudios.filter(e => e.estado === estado).length;
  }

  getEstudiosUrgentes(): number {
    return this.estudios.filter(e => e.urgente).length;
  }

  getEstudiosConContraste(): number {
    return this.estudios.filter(e => e.contraste).length;
  }

  // Métodos faltantes para el template
  getEstudiosStats(): any {
    return {
      total: this.estudios.length,
      programados: this.getEstudiosCountByEstado('Programado'),
      enProceso: this.getEstudiosCountByEstado('En Proceso'),
      completados: this.getEstudiosCountByEstado('Completado'),
      urgentes: this.getEstudiosUrgentes()
    };
  }

  getTodaysEstudios(): Estudio[] {
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    return this.estudios.filter(estudio => 
      estudio.fecha_realizacion?.startsWith(todayString) || false
    );
  }

  getModalidadName(modalidad: string | undefined): string {
    if (!modalidad) return 'No especificada';
    const modalidadNames: { [key: string]: string } = {
      'RX': 'Radiografía',
      'CT': 'Tomografía Computarizada',
      'MR': 'Resonancia Magnética',
      'US': 'Ultrasonido',
      'MG': 'Mamografía',
      'DX': 'Radiografía Digital',
      'XA': 'Angiografía',
      'PT': 'Tomografía por Emisión de Positrones',
      'NM': 'Medicina Nuclear',
      'RF': 'Radiología Fluoroscópica'
    };
    return modalidadNames[modalidad] || modalidad;
  }

  sortEstudiosByDate(): void {
    this.filteredEstudios.sort((a, b) => {
      const fechaA = a.fecha_realizacion ? new Date(a.fecha_realizacion).getTime() : 0;
      const fechaB = b.fecha_realizacion ? new Date(b.fecha_realizacion).getTime() : 0;
      return fechaB - fechaA;
    });
  }

  isToday(fecha: string | undefined): boolean {
    if (!fecha) return false;
    const fechaEstudio = new Date(fecha);
    const today = new Date();
    return fechaEstudio.toDateString() === today.toDateString();
  }

  isPending(estado: string): boolean {
    return ['Programado', 'En Proceso'].includes(estado);
  }
}
