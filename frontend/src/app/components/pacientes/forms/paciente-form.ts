import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { Api } from '../../../services/api';

export interface PacienteData {
  id?: number;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  fecha_nacimiento: string;
  tipo_documento: string;
  numero_documento: string;
  genero: string;
}

@Component({
  selector: 'app-paciente-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  template: `
    <h2 mat-dialog-title>{{ isEdit ? 'Editar' : 'Agregar' }} Paciente</h2>
    <mat-dialog-content>
      <form [formGroup]="pacienteForm" class="form-container">
        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Nombre completo</mat-label>
          <input matInput formControlName="nombre" placeholder="Ingrese el nombre completo">
          <mat-error *ngIf="pacienteForm.get('nombre')?.hasError('required')">
            El nombre es requerido
          </mat-error>
        </mat-form-field>

        <div class="row">
          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Tipo de documento</mat-label>
            <mat-select formControlName="tipo_documento">
              <mat-option value="CC">Cédula de Ciudadanía</mat-option>
              <mat-option value="TI">Tarjeta de Identidad</mat-option>
              <mat-option value="CE">Cédula de Extranjería</mat-option>
              <mat-option value="PP">Pasaporte</mat-option>
            </mat-select>
            <mat-error *ngIf="pacienteForm.get('tipo_documento')?.hasError('required')">
              Seleccione un tipo de documento
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Número de documento</mat-label>
            <input matInput formControlName="numero_documento" placeholder="123456789">
            <mat-error *ngIf="pacienteForm.get('numero_documento')?.hasError('required')">
              El número de documento es requerido
            </mat-error>
          </mat-form-field>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Email</mat-label>
          <input matInput type="email" formControlName="email" placeholder="correo@ejemplo.com">
          <mat-error *ngIf="pacienteForm.get('email')?.hasError('required')">
            El email es requerido
          </mat-error>
          <mat-error *ngIf="pacienteForm.get('email')?.hasError('email')">
            Ingrese un email válido
          </mat-error>
        </mat-form-field>

        <div class="row">
          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Teléfono</mat-label>
            <input matInput formControlName="telefono" placeholder="300 123 4567">
            <mat-error *ngIf="pacienteForm.get('telefono')?.hasError('required')">
              El teléfono es requerido
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Género</mat-label>
            <mat-select formControlName="genero">
              <mat-option value="Masculino">Masculino</mat-option>
              <mat-option value="Femenino">Femenino</mat-option>
              <mat-option value="Otro">Otro</mat-option>
            </mat-select>
            <mat-error *ngIf="pacienteForm.get('genero')?.hasError('required')">
              Seleccione un género
            </mat-error>
          </mat-form-field>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Fecha de nacimiento</mat-label>
          <input matInput [matDatepicker]="picker" formControlName="fecha_nacimiento">
          <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
          <mat-datepicker #picker></mat-datepicker>
          <mat-error *ngIf="pacienteForm.get('fecha_nacimiento')?.hasError('required')">
            La fecha de nacimiento es requerida
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Dirección</mat-label>
          <textarea matInput formControlName="direccion" rows="2" placeholder="Ingrese la dirección completa"></textarea>
          <mat-error *ngIf="pacienteForm.get('direccion')?.hasError('required')">
            La dirección es requerida
          </mat-error>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="onSave()" [disabled]="pacienteForm.invalid || isLoading">
        {{ isLoading ? 'Guardando...' : 'Guardar' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .form-container {
      padding: 1rem 0;
      max-width: 600px;
    }

    .full-width {
      width: 100%;
      margin-bottom: 1rem;
    }

    .row {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .half-width {
      flex: 1;
    }

    mat-dialog-content {
      max-height: 70vh;
      overflow-y: auto;
    }

    mat-dialog-actions {
      padding: 1rem 0;
    }
  `]
})
export class PacienteFormComponent implements OnInit {
  pacienteForm: FormGroup;
  isEdit: boolean = false;
  isLoading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private api: Api,
    public dialogRef: MatDialogRef<PacienteFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PacienteData
  ) {
    this.isEdit = !!data?.id;
    this.pacienteForm = this.createForm();
  }

  ngOnInit(): void {
    if (this.isEdit && this.data) {
      this.populateForm();
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      nombre: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required]],
      direccion: ['', [Validators.required]],
      fecha_nacimiento: ['', [Validators.required]],
      tipo_documento: ['CC', [Validators.required]],
      numero_documento: ['', [Validators.required]],
      genero: ['Masculino', [Validators.required]]
    });
  }

  private populateForm(): void {
    this.pacienteForm.patchValue({
      nombre: this.data.nombre,
      email: this.data.email,
      telefono: this.data.telefono,
      direccion: this.data.direccion,
      fecha_nacimiento: new Date(this.data.fecha_nacimiento),
      tipo_documento: this.data.tipo_documento,
      numero_documento: this.data.numero_documento,
      genero: this.data.genero
    });
  }

  onSave(): void {
    if (this.pacienteForm.valid) {
      this.isLoading = true;
      const formValue = { ...this.pacienteForm.value };

      // Convertir fecha a string ISO
      if (formValue.fecha_nacimiento) {
        formValue.fecha_nacimiento = formValue.fecha_nacimiento.toISOString();
      }

      // Simular guardado exitoso
      setTimeout(() => {
        this.isLoading = false;
        this.dialogRef.close(formValue);
      }, 1000);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
