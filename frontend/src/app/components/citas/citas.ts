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
import { FormsModule } from '@angular/forms';
import { CitaFormComponent } from './forms/cita-form';

export interface Cita {
  id: number;
  paciente_id: number;
  paciente_nombre: string;
  paciente_apellidos?: string;
  fecha_hora: string;
  tipo_estudio: string;
  estado: string;
  observaciones?: string;
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-citas',
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
    FormsModule,
  ],
  templateUrl: './citas.html',
  styleUrl: './citas.scss',
})
export class Citas implements OnInit {
  citas: Cita[] = [];
  filteredCitas: Cita[] = [];
  searchTerm: string = '';
  selectedEstado: string = 'Todos';
  selectedTipoEstudio: string = 'Todos';
  isLoading: boolean = true;

  estadoOptions = [
    'Todos',
    'Programada',
    'Confirmada',
    'En Proceso',
    'Completada',
    'Cancelada',
    'No Asistió',
  ];

  tipoEstudioOptions = [
    'Todos',
    'Radiografía',
    'Tomografía',
    'Resonancia Magnética',
    'Ecografía',
    'Mamografía',
    'Densitometría',
    'Angiografía',
    'PET/CT',
  ];

  constructor(
    private api: Api,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadCitas();
  }

  loadCitas(): void {
    this.isLoading = true;
    this.api.get('api/citas').subscribe({
      next: (response: any[]) => {
        console.log('Citas cargadas desde el backend:', response);
        this.citas = response.map(c => ({
          id: c.id,
          paciente_id: c.paciente_id,
          paciente_nombre: c.paciente_nombre,
          paciente_apellidos: c.paciente_apellidos,
          fecha_hora: c.fecha_cita,
          tipo_estudio: c.tipo_estudio,
          estado: c.estado,
          observaciones: c.observaciones,
          created_at: c.fecha_creacion,
          updated_at: c.fecha_actualizacion
        }));
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar citas:', error);
        // Fallback a datos de ejemplo si hay error de conexión
        this.citas = [
          {
            id: 1,
            paciente_id: 1,
            paciente_nombre: 'Juan',
            paciente_apellidos: 'Pérez González',
            fecha_hora: '2024-01-15T10:00:00',
            tipo_estudio: 'Radiografía',
            estado: 'Programada',
            observaciones: 'Radiografía de tórax'
          },
          {
            id: 2,
            paciente_id: 2,
            paciente_nombre: 'María',
            paciente_apellidos: 'García López',
            fecha_hora: '2024-01-15T14:00:00',
            tipo_estudio: 'Ecografía',
            estado: 'Confirmada',
            observaciones: 'Ecografía abdominal'
          }
        ];
        this.applyFilters();
        this.isLoading = false;
      }
    });
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(CitaFormComponent, {
      width: '700px',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadCitas();
        this.showMessage('Cita agendada exitosamente', 'success');
      }
    });
  }

  openEditDialog(cita: Cita): void {
    const dialogRef = this.dialog.open(CitaFormComponent, {
      width: '700px',
      data: cita,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadCitas();
        this.showMessage('Cita actualizada exitosamente', 'success');
      }
    });
  }

  deleteCita(cita: Cita): void {
    const nombreCompleto = `${cita.paciente_nombre} ${cita.paciente_apellidos || ''}`.trim();
    if (confirm(`¿Está seguro que desea eliminar la cita de ${nombreCompleto}?`)) {
      this.api.delete(`api/citas/${cita.id}`).subscribe({
        next: (response) => {
          console.log('Cita eliminada exitosamente:', response);
          this.loadCitas(); // Recargar la lista
          this.showMessage('Cita eliminada exitosamente', 'success');
        },
        error: (error) => {
          console.error('Error al eliminar cita:', error);
          this.showMessage(`Error al eliminar cita: ${error.error?.detail || error.message}`, 'error');
        }
      });
    }
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onEstadoChange(): void {
    this.applyFilters();
  }

  onTipoEstudioChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    console.log('Aplicando filtros - Datos originales:', this.citas.length);
    console.log('Filtros activos:', {
      searchTerm: this.searchTerm,
      selectedEstado: this.selectedEstado,
      selectedTipoEstudio: this.selectedTipoEstudio
    });
    
    let filtered = [...this.citas];

    // Filtro por término de búsqueda
    if (this.searchTerm && this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(
        (cita) =>
          (cita.paciente_nombre && cita.paciente_nombre.toLowerCase().includes(term)) ||
          (cita.paciente_apellidos && cita.paciente_apellidos.toLowerCase().includes(term)) ||
          (cita.tipo_estudio && cita.tipo_estudio.toLowerCase().includes(term)) ||
          (cita.observaciones && cita.observaciones.toLowerCase().includes(term))
      );
      console.log('Después de filtro de búsqueda:', filtered.length);
    }

    // Filtro por estado
    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      filtered = filtered.filter((cita) => cita.estado === this.selectedEstado);
      console.log('Después de filtro de estado:', filtered.length);
    }

    // Filtro por tipo de estudio
    if (this.selectedTipoEstudio && this.selectedTipoEstudio !== 'Todos') {
      filtered = filtered.filter((cita) => cita.tipo_estudio === this.selectedTipoEstudio);
      console.log('Después de filtro de tipo estudio:', filtered.length);
    }

    this.filteredCitas = filtered;
    console.log('Resultado final filtrado:', this.filteredCitas.length);
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case 'Programada':
        return 'estado-programada';
      case 'Confirmada':
        return 'estado-confirmada';
      case 'En Proceso':
        return 'estado-en-proceso';
      case 'Completada':
        return 'estado-completada';
      case 'Cancelada':
        return 'estado-cancelada';
      case 'No Asistió':
        return 'estado-no-asistio';
      default:
        return 'estado-default';
    }
  }

  formatFechaHora(fechaHora: string): { fecha: string; hora: string } {
    const date = new Date(fechaHora);
    return {
      fecha: date.toLocaleDateString('es-ES'),
      hora: date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
    };
  }

  isUpcoming(fechaHora: string): boolean {
    const citaDate = new Date(fechaHora);
    const now = new Date();
    const tomorrow = new Date();
    tomorrow.setDate(now.getDate() + 1);
    tomorrow.setHours(23, 59, 59, 999);

    return citaDate >= now && citaDate <= tomorrow;
  }

  sortCitasByDate(): void {
    this.filteredCitas.sort(
      (a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime(),
    );
  }

  getTodaysCitas(): Cita[] {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    return this.citas.filter((cita) => {
      const citaDate = new Date(cita.fecha_hora);
      return citaDate >= today && citaDate < tomorrow;
    });
  }

  getTodaysConfirmedCitas(): number {
    return this.getTodaysCitas().filter((c) => c.estado === 'Confirmada').length;
  }

  getTodaysProgrammedCitas(): number {
    return this.getTodaysCitas().filter((c) => c.estado === 'Programada').length;
  }

  trackByCitaId(index: number, cita: Cita): number {
    return cita.id;
  }

  isUrgent(fechaHora: string): boolean {
    const citaDate = new Date(fechaHora);
    const now = new Date();
    const twoHoursFromNow = new Date(now.getTime() + 2 * 60 * 60 * 1000);
    
    return citaDate >= now && citaDate <= twoHoursFromNow;
  }

  confirmCita(cita: Cita): void {
    const nombreCompleto = `${cita.paciente_nombre} ${cita.paciente_apellidos || ''}`.trim();
    if (confirm(`¿Confirmar la cita de ${nombreCompleto}?`)) {
      cita.estado = 'Confirmada';
      this.applyFilters();
      this.showMessage('Cita confirmada exitosamente', 'success');
    }
  }

  // Método para obtener el nombre completo del paciente
  getFullPatientName(cita: Cita): string {
    return `${cita.paciente_nombre} ${cita.paciente_apellidos || ''}`.trim();
  }
}
