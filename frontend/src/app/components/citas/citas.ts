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
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { FormsModule } from '@angular/forms';
import { CitaFormComponent } from './forms/cita-form';

export interface Cita {
  id: number;
  paciente_id: number;
  paciente_nombre: string;
  paciente_apellidos?: string;
  fecha_hora: string;
  tipo_estudio: string;
  tipo_cita: string;
  estado: string;
  observaciones?: string;
  medico_asignado?: string;
  sala?: string;
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
    MatDatepickerModule,
    MatNativeDateModule,
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
  selectedTipoCita: string = 'Todos';
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

  tipoCitaOptions = [
    'Todos',
    'Consulta General',
    'Control',
    'Urgente',
    'Especialista',
    'Seguimiento',
  ];

  constructor(
    private api: Api,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  // Variables para filtros con fechas
  selectedFecha: string = '';
  selectedDate: Date | null = null;

  ngOnInit(): void {
    this.loadCitas();
  }

  loadCitas(): void {
    this.isLoading = true;

    // Construir parámetros de filtro para el backend
    const params: any = {};

    if (this.selectedFecha && this.selectedFecha.trim()) {
      params.fecha = this.selectedFecha;
    }

    if (this.selectedEstado && this.selectedEstado !== 'Todos') {
      params.estado = this.selectedEstado;
    }

    if (this.selectedTipoEstudio && this.selectedTipoEstudio !== 'Todos') {
      params.tipo_estudio = this.selectedTipoEstudio;
    }

    if (this.selectedTipoCita && this.selectedTipoCita !== 'Todos') {
      params.tipo_cita = this.selectedTipoCita;
    }

    if (this.searchTerm && this.searchTerm.trim()) {
      params.paciente_nombre = this.searchTerm;
    }

    console.log('Parámetros de filtro enviados al backend:', params);

    this.api.get('api/citas', params).subscribe({
      next: (response: any[]) => {
        console.log('Citas cargadas desde el backend:', response);
        this.citas = response.map((c) => ({
          id: c.id,
          paciente_id: c.paciente_id,
          paciente_nombre: c.paciente_nombre,
          paciente_apellidos: c.paciente_apellidos || '',
          fecha_hora: c.fecha_cita,
          tipo_estudio: c.tipo_estudio,
          tipo_cita: c.tipo_cita || 'Consulta General',
          estado: c.estado,
          observaciones: c.observaciones,
          medico_asignado: c.medico_asignado,
          sala: c.sala,
          created_at: c.fecha_creacion,
          updated_at: c.fecha_actualizacion,
        }));
        this.filteredCitas = [...this.citas];
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
            tipo_cita: 'Consulta General',
            estado: 'Programada',
            observaciones: 'Radiografía de tórax',
            medico_asignado: 'Dr. García',
            sala: 'Sala 1',
          },
          {
            id: 2,
            paciente_id: 2,
            paciente_nombre: 'María',
            paciente_apellidos: 'García López',
            fecha_hora: '2024-01-15T14:00:00',
            tipo_estudio: 'Ecografía',
            tipo_cita: 'Control',
            estado: 'Confirmada',
            observaciones: 'Ecografía abdominal',
            medico_asignado: 'Dr. López',
            sala: 'Sala 2',
          },
        ];
        this.filteredCitas = [...this.citas];
        this.isLoading = false;
      },
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

  deleteCita(citaId: number): void {
    const cita = this.citas.find((c) => c.id === citaId);
    if (!cita) return;

    const nombreCompleto = `${cita.paciente_nombre} ${cita.paciente_apellidos || ''}`.trim();
    if (confirm(`¿Está seguro que desea eliminar la cita de ${nombreCompleto}?`)) {
      this.api.delete(`api/citas/${citaId}`).subscribe({
        next: (response) => {
          console.log('Cita eliminada exitosamente:', response);
          this.loadCitas(); // Recargar la lista
          this.showMessage('Cita eliminada exitosamente', 'success');
        },
        error: (error) => {
          console.error('Error al eliminar cita:', error);
          this.showMessage(
            `Error al eliminar cita: ${error.error?.detail || error.message}`,
            'error',
          );
        },
      });
    }
  }

  confirmCita(citaId: number): void {
    const cita = this.citas.find((c) => c.id === citaId);
    if (!cita) return;

    this.api.put(`api/citas/${citaId}`, { ...cita, estado: 'Confirmada' }).subscribe({
      next: (response) => {
        console.log('Cita confirmada exitosamente:', response);
        this.loadCitas();
        this.showMessage('Cita confirmada exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error al confirmar cita:', error);
        this.showMessage('Error al confirmar cita', 'error');
      },
    });
  }

  onSearchChange(): void {
    this.loadCitas();
  }

  onEstadoChange(): void {
    this.loadCitas();
  }

  onTipoEstudioChange(): void {
    this.loadCitas();
  }

  onTipoCitaChange(): void {
    this.loadCitas();
  }

  onFechaChange(): void {
    this.loadCitas();
  }

  onDatePickerChange(date: Date | null): void {
    if (date) {
      this.selectedFecha = date.toISOString().split('T')[0];
      this.selectedDate = date;
    } else {
      this.selectedFecha = '';
      this.selectedDate = null;
    }
    this.loadCitas();
  }

  setQuickDate(days: number): void {
    const date = new Date();
    date.setDate(date.getDate() + days);
    this.selectedDate = date;
    this.selectedFecha = date.toISOString().split('T')[0];
    this.loadCitas();
  }

  setToday(): void {
    this.setQuickDate(0);
  }

  setTomorrow(): void {
    this.setQuickDate(1);
  }

  setYesterday(): void {
    this.setQuickDate(-1);
  }

  clearDateFilter(): void {
    this.selectedFecha = '';
    this.selectedDate = null;
    this.loadCitas();
  }

  toggleSort(): void {
    this.filteredCitas.sort(
      (a, b) => new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime(),
    );
  }

  formatDateTime(dateTime: string): string {
    const date = new Date(dateTime);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedEstado = 'Todos';
    this.selectedTipoEstudio = 'Todos';
    this.selectedTipoCita = 'Todos';
    this.selectedFecha = '';
    this.selectedDate = null;
    this.loadCitas();
  }

  // Método auxiliar para filtros locales rápidos si se necesita
  private applyLocalFilter(term: string): void {
    if (!term || !term.trim()) {
      this.filteredCitas = [...this.citas];
      return;
    }

    const searchTerm = term.toLowerCase();
    this.filteredCitas = this.citas.filter(
      (cita) =>
        (cita.paciente_nombre && cita.paciente_nombre.toLowerCase().includes(searchTerm)) ||
        (cita.paciente_apellidos && cita.paciente_apellidos.toLowerCase().includes(searchTerm)) ||
        (cita.tipo_estudio && cita.tipo_estudio.toLowerCase().includes(searchTerm)) ||
        (cita.observaciones && cita.observaciones.toLowerCase().includes(searchTerm)),
    );
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

  // Método para obtener fecha de hoy en formato YYYY-MM-DD
  getTodayDate(): string {
    const today = new Date();
    return today.toISOString().split('T')[0];
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

  // Métodos helper para validar fechas
  isToday(date: Date | null): boolean {
    if (!date) return false;
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  }

  isTomorrow(date: Date | null): boolean {
    if (!date) return false;
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return (
      date.getDate() === tomorrow.getDate() &&
      date.getMonth() === tomorrow.getMonth() &&
      date.getFullYear() === tomorrow.getFullYear()
    );
  }

  isYesterday(date: Date | null): boolean {
    if (!date) return false;
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return (
      date.getDate() === yesterday.getDate() &&
      date.getMonth() === yesterday.getMonth() &&
      date.getFullYear() === yesterday.getFullYear()
    );
  }

  // Método para obtener el nombre completo del paciente
  getFullPatientName(cita: Cita): string {
    return `${cita.paciente_nombre} ${cita.paciente_apellidos || ''}`.trim();
  }
}
