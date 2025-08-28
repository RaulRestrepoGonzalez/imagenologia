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
  id: number;
  paciente_id: number;
  paciente_nombre: string;
  tipo_estudio: string;
  fecha_realizacion: string;
  estado: string;
  modalidad: string;
  parte_cuerpo: string;
  contraste: boolean;
  urgente: boolean;
  observaciones?: string;
  medico_referente?: string;
  created_at?: string;
  updated_at?: string;
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

  modalidadOptions = ['Todos', 'RX', 'CT', 'MR', 'US', 'MG', 'DX', 'XA', 'PT', 'NM', 'RF'];

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
    // Simular datos de ejemplo para demostración
    this.estudios = [
      {
        id: 1,
        paciente_id: 1,
        paciente_nombre: 'Juan Pérez',
        tipo_estudio: 'Radiografía de Tórax',
        fecha_realizacion: '2024-01-15T10:00:00',
        estado: 'Completado',
        modalidad: 'RX',
        parte_cuerpo: 'Tórax',
        contraste: false,
        urgente: false,
        observaciones: 'Radiografía PA y lateral',
        medico_referente: 'Dr. García'
      },
      {
        id: 2,
        paciente_id: 2,
        paciente_nombre: 'María García',
        tipo_estudio: 'Tomografía Abdominal',
        fecha_realizacion: '2024-01-15T14:00:00',
        estado: 'En Proceso',
        modalidad: 'CT',
        parte_cuerpo: 'Abdomen',
        contraste: true,
        urgente: true,
        observaciones: 'Con contraste IV',
        medico_referente: 'Dr. López'
      }
    ];
    this.applyFilters();
    this.isLoading = false;
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

  onUrgenciaChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    let filtered = [...this.estudios];

    // Filtro por término de búsqueda
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(
        (estudio) =>
          estudio.paciente_nombre.toLowerCase().includes(term) ||
          estudio.tipo_estudio.toLowerCase().includes(term) ||
          estudio.observaciones?.toLowerCase().includes(term),
      );
    }

    // Filtro por estado
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      filtered = filtered.filter((estudio) => estudio.estado === this.selectedEstado);
    }

    // Filtro por modalidad
    if (this.selectedModalidad && this.selectedModalidad !== 'Todos') {
      filtered = filtered.filter((estudio) => estudio.modalidad === this.selectedModalidad);
    }

    // Filtro por urgencia
    if (this.selectedUrgencia && this.selectedUrgencia !== 'Todos') {
      const isUrgente = this.selectedUrgencia === 'Urgente';
      filtered = filtered.filter((estudio) => estudio.urgente === isUrgente);
    }

    this.filteredEstudios = filtered;
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
      estudio.fecha_realizacion.startsWith(todayString)
    );
  }

  getModalidadName(modalidad: string): string {
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
    this.filteredEstudios.sort((a, b) => 
      new Date(b.fecha_realizacion).getTime() - new Date(a.fecha_realizacion).getTime()
    );
  }

  isToday(fecha: string): boolean {
    const fechaEstudio = new Date(fecha);
    const today = new Date();
    return fechaEstudio.toDateString() === today.toDateString();
  }

  isPending(estado: string): boolean {
    return ['Programado', 'En Proceso'].includes(estado);
  }
}
