import { Component, OnInit } from '@angular/core';
import { Api } from '../../services/api';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { PacienteFormComponent } from './forms/paciente-form';

export interface Paciente {
  id: number;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  fecha_nacimiento: string;
  tipo_documento: string;
  numero_documento: string;
  genero: string;
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-pacientes',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatDialogModule,
    MatIconModule,
    MatSnackBarModule,
    MatTableModule,
    MatInputModule,
    MatFormFieldModule,
    FormsModule,
  ],
  templateUrl: './pacientes.html',
  styleUrl: './pacientes.scss',
})
export class Pacientes implements OnInit {
  pacientes: Paciente[] = [];
  filteredPacientes: Paciente[] = [];
  searchTerm: string = '';
  isLoading: boolean = true;

  constructor(
    private api: Api,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadPacientes();
  }

  loadPacientes(): void {
    this.isLoading = true;
    // Simular datos de ejemplo para demostración
    this.pacientes = [
      {
        id: 1,
        nombre: 'Juan Pérez',
        email: 'juan.perez@email.com',
        telefono: '3001234567',
        direccion: 'Calle 123 #45-67',
        fecha_nacimiento: '1985-03-15',
        tipo_documento: 'CC',
        numero_documento: '12345678',
        genero: 'Masculino'
      },
      {
        id: 2,
        nombre: 'María García',
        email: 'maria.garcia@email.com',
        telefono: '3009876543',
        direccion: 'Carrera 78 #90-12',
        fecha_nacimiento: '1990-07-22',
        tipo_documento: 'CC',
        numero_documento: '87654321',
        genero: 'Femenino'
      }
    ];
    this.filteredPacientes = [...this.pacientes];
    this.isLoading = false;
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(PacienteFormComponent, {
      width: '600px',
      data: {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadPacientes();
        this.showMessage('Paciente agregado exitosamente', 'success');
      }
    });
  }

  openEditDialog(paciente: Paciente): void {
    const dialogRef = this.dialog.open(PacienteFormComponent, {
      width: '600px',
      data: paciente,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadPacientes();
        this.showMessage('Paciente actualizado exitosamente', 'success');
      }
    });
  }

  deletePaciente(paciente: Paciente): void {
    if (confirm(`¿Está seguro que desea eliminar al paciente ${paciente.nombre}?`)) {
      this.pacientes = this.pacientes.filter(p => p.id !== paciente.id);
      this.filteredPacientes = [...this.pacientes];
      this.showMessage('Paciente eliminado exitosamente', 'success');
    }
  }

  onSearchChange(): void {
    this.filteredPacientes = this.pacientes.filter(paciente =>
      paciente.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      paciente.numero_documento.includes(this.searchTerm) ||
      paciente.email.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  // Métodos faltantes para el template
  getDocumentTypeText(tipo: string): string {
    const documentTypes: { [key: string]: string } = {
      'CC': 'Cédula de Ciudadanía',
      'CE': 'Cédula de Extranjería',
      'TI': 'Tarjeta de Identidad',
      'PP': 'Pasaporte',
      'RC': 'Registro Civil',
      'NIT': 'Número de Identificación Tributaria'
    };
    return documentTypes[tipo] || tipo;
  }

  getGenderText(genero: string): string {
    const genderTypes: { [key: string]: string } = {
      'Masculino': 'M',
      'Femenino': 'F',
      'Otro': 'O',
      'No especificado': 'N/A'
    };
    return genderTypes[genero] || genero;
  }
}
