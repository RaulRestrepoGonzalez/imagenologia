import { Component, OnInit } from '@angular/core';
import { Api } from '../../services/api';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { CommonModule } from '@angular/common';

export interface Notificacion {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  fecha: string;
  leida: boolean;
  prioridad: 'baja' | 'media' | 'alta';
  destinatario: string;
  accion_requerida?: string;
}

@Component({
  selector: 'app-notificaciones',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule, MatButtonToggleModule],
  templateUrl: './notificaciones.html',
  styleUrl: './notificaciones.scss',
})
export class Notificaciones implements OnInit {
  notificaciones: Notificacion[] = [];
  filteredNotificaciones: Notificacion[] = [];
  selectedTipo: string = 'Todas';
  selectedPrioridad: string = 'Todas';
  showLeidas: boolean = true;

  tipoOptions = ['Todas', 'Cita', 'Estudio', 'Informe', 'Sistema', 'Recordatorio'];
  prioridadOptions = ['Todas', 'Baja', 'Media', 'Alta'];

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.loadNotificaciones();
  }

  loadNotificaciones(): void {
    // Simular datos de ejemplo para demostración
    this.notificaciones = [
      {
        id: 1,
        tipo: 'Cita',
        titulo: 'Cita Programada',
        mensaje: 'Su cita para Radiografía de Tórax ha sido programada para mañana a las 10:00 AM',
        fecha: '2024-01-15T09:00:00',
        leida: false,
        prioridad: 'media',
        destinatario: 'Juan Pérez'
      },
      {
        id: 2,
        tipo: 'Estudio',
        titulo: 'Estudio Completado',
        mensaje: 'El estudio de Tomografía Abdominal ha sido completado y está listo para interpretación',
        fecha: '2024-01-15T14:30:00',
        leida: false,
        prioridad: 'alta',
        destinatario: 'Dr. Martínez'
      },
      {
        id: 3,
        tipo: 'Informe',
        titulo: 'Informe Validado',
        mensaje: 'El informe de Radiografía de Tórax ha sido validado y está disponible para el paciente',
        fecha: '2024-01-15T16:00:00',
        leida: true,
        prioridad: 'baja',
        destinatario: 'Dr. Rodríguez'
      },
      {
        id: 4,
        tipo: 'Sistema',
        titulo: 'Mantenimiento Programado',
        mensaje: 'El sistema estará en mantenimiento el próximo domingo de 2:00 AM a 6:00 AM',
        fecha: '2024-01-15T08:00:00',
        leida: true,
        prioridad: 'media',
        destinatario: 'Todos los usuarios'
      }
    ];
    this.applyFilters();
  }

  applyFilters(): void {
    let filtered = [...this.notificaciones];

    // Filtro por tipo
    if (this.selectedTipo && this.selectedTipo !== 'Todas') {
      filtered = filtered.filter(n => n.tipo === this.selectedTipo);
    }

    // Filtro por prioridad
    if (this.selectedPrioridad && this.selectedPrioridad !== 'Todas') {
      const prioridad = this.selectedPrioridad.toLowerCase();
      filtered = filtered.filter(n => n.prioridad === prioridad);
    }

    // Filtro por estado de lectura
    if (!this.showLeidas) {
      filtered = filtered.filter(n => !n.leida);
    }

    this.filteredNotificaciones = filtered;
  }

  onTipoChange(): void {
    this.applyFilters();
  }

  onPrioridadChange(): void {
    this.applyFilters();
  }

  onShowLeidasChange(): void {
    this.applyFilters();
  }

  marcarComoLeida(notificacion: Notificacion): void {
    notificacion.leida = true;
    this.applyFilters();
  }

  marcarTodasComoLeidas(): void {
    this.notificaciones.forEach(n => n.leida = true);
    this.applyFilters();
  }

  eliminarNotificacion(notificacion: Notificacion): void {
    if (confirm('¿Está seguro que desea eliminar esta notificación?')) {
      this.notificaciones = this.notificaciones.filter(n => n.id !== notificacion.id);
      this.applyFilters();
    }
  }

  getPrioridadClass(prioridad: string): string {
    switch (prioridad) {
      case 'alta':
        return 'prioridad-alta';
      case 'media':
        return 'prioridad-media';
      case 'baja':
        return 'prioridad-baja';
      default:
        return 'prioridad-default';
    }
  }

  getTipoIcon(tipo: string): string {
    switch (tipo) {
      case 'Cita':
        return 'event';
      case 'Estudio':
        return 'science';
      case 'Informe':
        return 'description';
      case 'Sistema':
        return 'computer';
      case 'Recordatorio':
        return 'notifications';
      default:
        return 'info';
    }
  }

  formatFecha(fecha: string): string {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getNotificacionesNoLeidas(): number {
    return this.notificaciones.filter(n => !n.leida).length;
  }

  getNotificacionesPorTipo(tipo: string): number {
    return this.notificaciones.filter(n => n.tipo === tipo).length;
  }

  getNotificacionesPorPrioridad(prioridad: string): number {
    return this.notificaciones.filter(n => n.prioridad === prioridad).length;
  }
}
