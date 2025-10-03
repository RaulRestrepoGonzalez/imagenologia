import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { Api } from '../../../services/api';

export interface EstudioData {
  id?: string;
  paciente_id: string;
  tipo_estudio: string;
  medico_solicitante: string;
  prioridad: string;
  indicaciones?: string;
  sala?: string;
  tecnico_asignado?: string;
  estado?: string;
  fecha_solicitud?: string;
  fecha_programada?: string;
  fecha_realizacion?: string;
  resultados?: string;
  paciente_nombre?: string;
}

export interface Paciente {
  id: number;
  nombre: string;
  numero_documento: string;
  tipo_documento: string;
  edad?: number;
}

@Component({
  selector: 'app-estudio-form',
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
    MatNativeDateModule,
    MatIconModule,
    MatCheckboxModule
  ],
  template: `
    <h2 mat-dialog-title>{{ isEdit ? 'Editar' : 'Nuevo' }} Estudio</h2>
    <mat-dialog-content>
      <form [formGroup]="estudioForm" class="form-container">
        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Paciente</mat-label>
          <mat-select formControlName="paciente_id" [disabled]="isLoadingPacientes">
            <mat-option *ngIf="isLoadingPacientes" disabled>
              Cargando pacientes...
            </mat-option>
            <mat-option *ngFor="let paciente of pacientes" [value]="paciente.id">
              {{ paciente.nombre }} - {{ paciente.tipo_documento }}: {{ paciente.numero_documento }}
            </mat-option>
          </mat-select>
          <mat-error *ngIf="estudioForm.get('paciente_id')?.hasError('required')">
            Seleccione un paciente
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Tipo de Estudio</mat-label>
          <mat-select formControlName="tipo_estudio">
            <mat-option value="Radiografía">Radiografía</mat-option>
            <mat-option value="Tomografía Computarizada">Tomografía Computarizada</mat-option>
            <mat-option value="Resonancia Magnética">Resonancia Magnética</mat-option>
            <mat-option value="Ecografía">Ecografía</mat-option>
            <mat-option value="Mamografía">Mamografía</mat-option>
            <mat-option value="Densitometría Ósea">Densitometría Ósea</mat-option>
            <mat-option value="Angiografía">Angiografía</mat-option>
            <mat-option value="PET/CT">PET/CT</mat-option>
            <mat-option value="SPECT">SPECT</mat-option>
            <mat-option value="Fluoroscopia">Fluoroscopia</mat-option>
          </mat-select>
          <mat-error *ngIf="estudioForm.get('tipo_estudio')?.hasError('required')">
            Seleccione un tipo de estudio
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Médico Solicitante</mat-label>
          <input matInput formControlName="medico_solicitante" placeholder="Dr(a). Nombre del médico solicitante">
          <mat-error *ngIf="estudioForm.get('medico_solicitante')?.hasError('required')">
            El médico solicitante es requerido
          </mat-error>
        </mat-form-field>

        <div class="row">
          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Prioridad</mat-label>
            <mat-select formControlName="prioridad">
              <mat-option value="baja">Baja</mat-option>
              <mat-option value="normal">Normal</mat-option>
              <mat-option value="alta">Alta</mat-option>
              <mat-option value="urgente">Urgente</mat-option>
            </mat-select>
            <mat-error *ngIf="estudioForm.get('prioridad')?.hasError('required')">
              Seleccione una prioridad
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Sala</mat-label>
            <mat-select formControlName="sala">
              <mat-option value="Sala 1">Sala 1</mat-option>
              <mat-option value="Sala 2">Sala 2</mat-option>
              <mat-option value="Sala 3">Sala 3</mat-option>
              <mat-option value="Sala CT">Sala CT</mat-option>
              <mat-option value="Sala RM">Sala RM</mat-option>
              <mat-option value="Sala Eco">Sala Eco</mat-option>
            </mat-select>
          </mat-form-field>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Fecha de Realización</mat-label>
          <input 
            matInput 
            [matDatepicker]="fechaPicker" 
            formControlName="fecha_realizacion"
            placeholder="Seleccione la fecha del estudio"
          />
          <mat-datepicker-toggle matIconSuffix [for]="fechaPicker"></mat-datepicker-toggle>
          <mat-datepicker #fechaPicker></mat-datepicker>
          <mat-hint>Fecha en la que se realizará o se realizó el estudio</mat-hint>
          <mat-error *ngIf="estudioForm.get('fecha_realizacion')?.hasError('required')">
            La fecha de realización es requerida
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Técnico Asignado</mat-label>
          <input matInput formControlName="tecnico_asignado" placeholder="Nombre del técnico asignado (opcional)">
        </mat-form-field>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Indicaciones</mat-label>
          <textarea
            matInput
            formControlName="indicaciones"
            rows="3"
            placeholder="Indicaciones médicas o instrucciones especiales (opcional)">
          </textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="onSave()" [disabled]="isLoading">
        {{ isLoading ? 'Guardando...' : 'Guardar' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .form-container {
      padding: 1rem 0;
      max-width: 700px;
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
      max-height: 80vh;
      overflow-y: auto;
    }

    mat-dialog-actions {
      padding: 1rem 0;
    }

    mat-option {
      font-size: 0.9rem;
    }

    @media (max-width: 600px) {
      .row {
        flex-direction: column;
      }
    }
  `]
})
export class EstudioFormComponent implements OnInit {
  estudioForm: FormGroup;
  isEdit: boolean = false;
  isLoading: boolean = false;
  isLoadingPacientes: boolean = true;
  pacientes: Paciente[] = [];

  constructor(
    private fb: FormBuilder,
    private api: Api,
    public dialogRef: MatDialogRef<EstudioFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EstudioData
  ) {
    this.isEdit = !!data?.id;
    this.estudioForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadPacientes();
    if (this.isEdit && this.data) {
      this.populateForm();
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      paciente_id: ['', [Validators.required]],
      tipo_estudio: ['', [Validators.required]],
      medico_solicitante: ['', [Validators.required]],
      prioridad: ['normal', [Validators.required]],
      fecha_realizacion: ['', [Validators.required]],
      indicaciones: [''],
      sala: [''],
      tecnico_asignado: ['']
    });
  }

  private loadPacientes(): void {
    this.isLoadingPacientes = true;
    this.api.get('api/pacientes').subscribe({
      next: (data: Paciente[]) => {
        this.pacientes = data;
        this.isLoadingPacientes = false;
      },
      error: (error) => {
        console.error('Error loading patients:', error);
        this.isLoadingPacientes = false;
      }
    });
  }

  private populateForm(): void {
    const fechaRealizacion = this.data.fecha_realizacion 
      ? new Date(this.data.fecha_realizacion) 
      : null;

    this.estudioForm.patchValue({
      paciente_id: this.data.paciente_id,
      tipo_estudio: this.data.tipo_estudio,
      medico_solicitante: this.data.medico_solicitante || '',
      prioridad: this.data.prioridad || 'normal',
      fecha_realizacion: fechaRealizacion,
      indicaciones: this.data.indicaciones || '',
      sala: this.data.sala || '',
      tecnico_asignado: this.data.tecnico_asignado || ''
    });
  }

  onSave(): void {
    if (this.estudioForm.invalid) {
      console.error('Formulario inválido:', this.estudioForm.errors);
      Object.keys(this.estudioForm.controls).forEach(key => {
        const control = this.estudioForm.get(key);
        if (control?.invalid) {
          console.error(`Campo inválido: ${key}`, control.errors);
        }
      });
      alert('Por favor complete todos los campos requeridos');
      return;
    }

    this.isLoading = true;
    const formValue = { ...this.estudioForm.value };

    // Convertir la fecha al formato correcto (YYYY-MM-DD)
    if (formValue.fecha_realizacion) {
      const fecha = new Date(formValue.fecha_realizacion);
      const year = fecha.getFullYear();
      const month = String(fecha.getMonth() + 1).padStart(2, '0');
      const day = String(fecha.getDate()).padStart(2, '0');
      formValue.fecha_realizacion = `${year}-${month}-${day}`;
      console.log('Fecha convertida:', formValue.fecha_realizacion);
    }

    console.log('Datos completos enviados al backend:', formValue);

    const operation = this.isEdit
      ? this.api.put(`api/estudios/${this.data.id}`, formValue)
      : this.api.post('api/estudios', formValue);

    operation.subscribe({
      next: (response) => {
        console.log('Respuesta del backend completa:', response);
        console.log('Fecha guardada en el backend:', response.fecha_realizacion);
        this.isLoading = false;
        this.dialogRef.close(response);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error al guardar estudio:', error);
        console.error('Detalles del error:', error.error);
        alert(`Error al guardar: ${error.error?.detail || error.message}`);
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}