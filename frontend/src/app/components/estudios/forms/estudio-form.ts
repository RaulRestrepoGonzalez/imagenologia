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
  id?: number;
  paciente_id: number;
  tipo_estudio: string;
  fecha_realizacion: string;
  estado: string;
  modalidad: string;
  parte_cuerpo: string;
  contraste: boolean;
  observaciones?: string;
  medico_referente?: string;
  urgente: boolean;
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

        <div class="row">
          <mat-form-field appearance="fill" class="half-width">
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

          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Modalidad</mat-label>
            <mat-select formControlName="modalidad">
              <mat-option value="RX">RX - Rayos X</mat-option>
              <mat-option value="CT">CT - Tomografía</mat-option>
              <mat-option value="MR">MR - Resonancia</mat-option>
              <mat-option value="US">US - Ultrasonido</mat-option>
              <mat-option value="MG">MG - Mamografía</mat-option>
              <mat-option value="DX">DX - Densitometría</mat-option>
              <mat-option value="XA">XA - Angiografía</mat-option>
              <mat-option value="PT">PT - PET</mat-option>
              <mat-option value="NM">NM - Medicina Nuclear</mat-option>
              <mat-option value="RF">RF - Fluoroscopia</mat-option>
            </mat-select>
            <mat-error *ngIf="estudioForm.get('modalidad')?.hasError('required')">
              Seleccione una modalidad
            </mat-error>
          </mat-form-field>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Parte del Cuerpo</mat-label>
          <mat-select formControlName="parte_cuerpo">
            <mat-option value="Cabeza">Cabeza</mat-option>
            <mat-option value="Cuello">Cuello</mat-option>
            <mat-option value="Tórax">Tórax</mat-option>
            <mat-option value="Abdomen">Abdomen</mat-option>
            <mat-option value="Pelvis">Pelvis</mat-option>
            <mat-option value="Extremidad Superior">Extremidad Superior</mat-option>
            <mat-option value="Extremidad Inferior">Extremidad Inferior</mat-option>
            <mat-option value="Columna Vertebral">Columna Vertebral</mat-option>
            <mat-option value="Corazón">Corazón</mat-option>
            <mat-option value="Sistema Vascular">Sistema Vascular</mat-option>
            <mat-option value="Todo el Cuerpo">Todo el Cuerpo</mat-option>
          </mat-select>
          <mat-error *ngIf="estudioForm.get('parte_cuerpo')?.hasError('required')">
            Seleccione la parte del cuerpo
          </mat-error>
        </mat-form-field>

        <div class="row">
          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Fecha de Realización</mat-label>
            <input matInput [matDatepicker]="picker" formControlName="fecha_realizacion">
            <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
            <mat-datepicker #picker></mat-datepicker>
            <mat-error *ngIf="estudioForm.get('fecha_realizacion')?.hasError('required')">
              La fecha es requerida
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="fill" class="half-width">
            <mat-label>Estado</mat-label>
            <mat-select formControlName="estado">
              <mat-option value="Programado">Programado</mat-option>
              <mat-option value="En Proceso">En Proceso</mat-option>
              <mat-option value="Completado">Completado</mat-option>
              <mat-option value="Interpretado">Interpretado</mat-option>
              <mat-option value="Informado">Informado</mat-option>
              <mat-option value="Entregado">Entregado</mat-option>
              <mat-option value="Cancelado">Cancelado</mat-option>
            </mat-select>
            <mat-error *ngIf="estudioForm.get('estado')?.hasError('required')">
              Seleccione un estado
            </mat-error>
          </mat-form-field>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Médico Referente</mat-label>
          <input matInput formControlName="medico_referente" placeholder="Dr(a). Nombre del médico">
        </mat-form-field>

        <div class="checkboxes-row">
          <mat-checkbox formControlName="contraste">
            <span class="checkbox-label">Requiere contraste</span>
          </mat-checkbox>

          <mat-checkbox formControlName="urgente">
            <span class="checkbox-label">Estudio urgente</span>
          </mat-checkbox>
        </div>

        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Observaciones</mat-label>
          <textarea
            matInput
            formControlName="observaciones"
            rows="3"
            placeholder="Ingrese observaciones adicionales (opcional)">
          </textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="onSave()" [disabled]="estudioForm.invalid || isLoading">
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

    .checkboxes-row {
      display: flex;
      gap: 2rem;
      margin: 1.5rem 0;
      flex-wrap: wrap;
    }

    .checkbox-label {
      font-size: 0.95rem;
      color: #333;
      margin-left: 0.5rem;
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

    mat-checkbox {
      display: flex;
      align-items: center;
    }

    .mat-mdc-checkbox .mdc-checkbox {
      padding: 8px;
    }

    @media (max-width: 600px) {
      .row {
        flex-direction: column;
      }

      .checkboxes-row {
        flex-direction: column;
        gap: 1rem;
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
      modalidad: ['', [Validators.required]],
      parte_cuerpo: ['', [Validators.required]],
      fecha_realizacion: ['', [Validators.required]],
      estado: ['Programado', [Validators.required]],
      medico_referente: [''],
      contraste: [false],
      urgente: [false],
      observaciones: ['']
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
    if (this.data.fecha_realizacion) {
      const fecha = new Date(this.data.fecha_realizacion);

      this.estudioForm.patchValue({
        paciente_id: this.data.paciente_id,
        tipo_estudio: this.data.tipo_estudio,
        modalidad: this.data.modalidad,
        parte_cuerpo: this.data.parte_cuerpo,
        fecha_realizacion: fecha,
        estado: this.data.estado,
        medico_referente: this.data.medico_referente || '',
        contraste: this.data.contraste || false,
        urgente: this.data.urgente || false,
        observaciones: this.data.observaciones || ''
      });
    }
  }

  onSave(): void {
    if (this.estudioForm.valid) {
      this.isLoading = true;
      const formValue = { ...this.estudioForm.value };

      // Formatear fecha
      if (formValue.fecha_realizacion instanceof Date) {
        formValue.fecha_realizacion = formValue.fecha_realizacion.toISOString().split('T')[0];
      }

      const operation = this.isEdit
        ? this.api.put(`api/estudios/${this.data.id}`, formValue)
        : this.api.post('api/estudios', formValue);

      operation.subscribe({
        next: (response) => {
          this.isLoading = false;
          this.dialogRef.close(response);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error al guardar estudio:', error);
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
