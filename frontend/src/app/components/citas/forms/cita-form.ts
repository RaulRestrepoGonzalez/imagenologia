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
import { MatIconModule } from '@angular/material/icon';
import { Api } from '../../../services/api';

export interface CitaData {
  id?: number;
  paciente_id: number;
  fecha_hora: string;
  tipo_estudio: string;
  estado: string;
  observaciones?: string;
  paciente_nombre?: string;
}

export interface Paciente {
  id: number;
  nombre: string;
  numero_documento: string;
  tipo_documento: string;
}

@Component({
  selector: 'app-cita-form',
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
    MatIconModule
  ],
  template: `
    <div class="form-dialog">
      <div class="dialog-header">
        <h2 mat-dialog-title class="dialog-title">
          <mat-icon class="title-icon">{{ isEdit ? 'edit' : 'add' }}</mat-icon>
          {{ isEdit ? 'Editar' : 'Agendar' }} Cita
        </h2>
        <p class="dialog-subtitle">
          {{ isEdit ? 'Modifica los datos de la cita' : 'Completa la información para agendar una nueva cita' }}
        </p>
      </div>
      
      <mat-dialog-content class="dialog-content">
        <form [formGroup]="citaForm" class="form-container">
          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>person</mat-icon>
              Información del Paciente
            </h3>
            
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Paciente</mat-label>
              <mat-select formControlName="paciente_id" [disabled]="isLoadingPacientes">
                <mat-option *ngIf="isLoadingPacientes" disabled>
                  <div class="loading-option">
                    <mat-icon class="loading-spinner">hourglass_empty</mat-icon>
                    Cargando pacientes...
                  </div>
                </mat-option>
                <mat-option *ngFor="let paciente of pacientes" [value]="paciente.id">
                  <div class="paciente-option">
                    <div class="paciente-info">
                      <span class="paciente-nombre">{{ paciente.nombre }}</span>
                      <span class="paciente-documento">{{ paciente.tipo_documento }}: {{ paciente.numero_documento }}</span>
                    </div>
                  </div>
                </mat-option>
              </mat-select>
              <mat-error *ngIf="citaForm.get('paciente_id')?.hasError('required')">
                Seleccione un paciente
              </mat-error>
            </mat-form-field>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>schedule</mat-icon>
              Fecha y Hora
            </h3>
            
            <div class="datetime-row">
              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Fecha</mat-label>
                <input matInput [matDatepicker]="picker" formControlName="fecha" [min]="minDate">
                <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
                <mat-datepicker #picker></mat-datepicker>
                <mat-error *ngIf="citaForm.get('fecha')?.hasError('required')">
                  La fecha es requerida
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Hora</mat-label>
                <input matInput type="time" formControlName="hora" min="07:00" max="18:00">
                <mat-error *ngIf="citaForm.get('hora')?.hasError('required')">
                  La hora es requerida
                </mat-error>
              </mat-form-field>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>medical_services</mat-icon>
              Detalles del Estudio
            </h3>
            
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Tipo de Estudio</mat-label>
              <mat-select formControlName="tipo_estudio">
                <mat-option value="Radiografía">
                  <div class="estudio-option">
                    <mat-icon>photo_camera</mat-icon>
                    <span>Radiografía</span>
                  </div>
                </mat-option>
                <mat-option value="Tomografía">
                  <div class="estudio-option">
                    <mat-icon>scanner</mat-icon>
                    <span>Tomografía</span>
                  </div>
                </mat-option>
                <mat-option value="Resonancia Magnética">
                  <div class="estudio-option">
                    <mat-icon>magnet</mat-icon>
                    <span>Resonancia Magnética</span>
                  </div>
                </mat-option>
                <mat-option value="Ecografía">
                  <div class="estudio-option">
                    <mat-icon>waves</mat-icon>
                    <span>Ecografía</span>
                  </div>
                </mat-option>
                <mat-option value="Mamografía">
                  <div class="estudio-option">
                    <mat-icon>healing</mat-icon>
                    <span>Mamografía</span>
                  </div>
                </mat-option>
                <mat-option value="Densitometría">
                  <div class="estudio-option">
                    <mat-icon>straighten</mat-icon>
                    <span>Densitometría</span>
                  </div>
                </mat-option>
                <mat-option value="Angiografía">
                  <div class="estudio-option">
                    <mat-icon>timeline</mat-icon>
                    <span>Angiografía</span>
                  </div>
                </mat-option>
                <mat-option value="PET/CT">
                  <div class="estudio-option">
                    <mat-icon>radar</mat-icon>
                    <span>PET/CT</span>
                  </div>
                </mat-option>
              </mat-select>
              <mat-error *ngIf="citaForm.get('tipo_estudio')?.hasError('required')">
                Seleccione un tipo de estudio
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Estado</mat-label>
              <mat-select formControlName="estado">
                <mat-option value="programada">
                  <div class="estado-option programada">
                    <mat-icon>schedule</mat-icon>
                    <span>Programada</span>
                  </div>
                </mat-option>
                <mat-option value="en_proceso">
                  <div class="estado-option en-proceso">
                    <mat-icon>play_circle</mat-icon>
                    <span>En Proceso</span>
                  </div>
                </mat-option>
                <mat-option value="completada">
                  <div class="estado-option completada">
                    <mat-icon>done_all</mat-icon>
                    <span>Completada</span>
                  </div>
                </mat-option>
                <mat-option value="cancelada">
                  <div class="estado-option cancelada">
                    <mat-icon>cancel</mat-icon>
                    <span>Cancelada</span>
                  </div>
                </mat-option>
                <mat-option value="no_asistio">
                  <div class="estado-option no-asistio">
                    <mat-icon>person_off</mat-icon>
                    <span>No Asistió</span>
                  </div>
                </mat-option>
              </mat-select>
              <mat-error *ngIf="citaForm.get('estado')?.hasError('required')">
                Seleccione un estado
              </mat-error>
            </mat-form-field>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>settings</mat-icon>
              Configuración Adicional
            </h3>
            
            <div class="datetime-row">
              <mat-form-field appearance="outline" class="half-width">
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

              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Duración (minutos)</mat-label>
                <input matInput type="number" formControlName="duracion_minutos" min="15" max="180">
                <mat-error *ngIf="citaForm.get('duracion_minutos')?.hasError('min')">
                  Mínimo 15 minutos
                </mat-error>
                <mat-error *ngIf="citaForm.get('duracion_minutos')?.hasError('max')">
                  Máximo 180 minutos
                </mat-error>
              </mat-form-field>
            </div>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Técnico Asignado</mat-label>
              <input matInput formControlName="tecnico_asignado" placeholder="Nombre del técnico asignado (opcional)">
            </mat-form-field>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>notes</mat-icon>
              Observaciones Adicionales
            </h3>
            
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Observaciones</mat-label>
              <textarea
                matInput
                formControlName="observaciones"
                rows="4"
                placeholder="Ingrese observaciones adicionales, instrucciones especiales o notas importantes para el estudio...">
              </textarea>
              <mat-hint>Opcional: Agregue información adicional relevante para el estudio</mat-hint>
            </mat-form-field>
          </div>
        </form>
      </mat-dialog-content>
      
      <mat-dialog-actions class="dialog-actions">
        <button mat-button (click)="onCancel()" class="cancel-button">
          <mat-icon>close</mat-icon>
          Cancelar
        </button>
        <button mat-raised-button color="primary" (click)="onSave()" [disabled]="citaForm.invalid || isLoading" class="save-button">
          <mat-icon *ngIf="!isLoading">{{ isEdit ? 'save' : 'add' }}</mat-icon>
          <mat-icon *ngIf="isLoading" class="loading-spinner">hourglass_empty</mat-icon>
          {{ isLoading ? 'Guardando...' : (isEdit ? 'Actualizar' : 'Agendar') }}
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .form-dialog {
      max-width: 700px;
      width: 100%;
    }

    .dialog-header {
      text-align: center;
      padding: 24px 0 16px 0;
      border-bottom: 1px solid var(--border-light);
      margin-bottom: 24px;
    }

    .dialog-title {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--gray-900);
      margin: 0 0 8px 0;
    }

    .title-icon {
      color: var(--primary-600);
      font-size: 1.75rem;
      width: 1.75rem;
      height: 1.75rem;
    }

    .dialog-subtitle {
      color: var(--gray-600);
      font-size: 1rem;
      margin: 0;
      line-height: 1.5;
    }

    .dialog-content {
      max-height: 70vh;
      overflow-y: auto;
      padding: 0;
    }

    .form-container {
      padding: 0;
    }

    .form-section {
      margin-bottom: 32px;
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 1.125rem;
      font-weight: 600;
      color: var(--gray-800);
      margin: 0 0 20px 0;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--primary-100);
    }

    .section-title mat-icon {
      color: var(--primary-600);
      font-size: 1.25rem;
      width: 1.25rem;
      height: 1.25rem;
    }

    .full-width {
      width: 100%;
      margin-bottom: 20px;
    }

    .datetime-row {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
    }

    .half-width {
      flex: 1;
    }

    .loading-option {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--gray-500);
    }

    .loading-spinner {
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .paciente-option {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .paciente-info {
      display: flex;
      flex-direction: column;
    }

    .paciente-nombre {
      font-weight: 500;
      color: var(--gray-900);
    }

    .paciente-documento {
      font-size: 0.875rem;
      color: var(--gray-600);
    }

    .estudio-option {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .estudio-option mat-icon {
      color: var(--primary-600);
      font-size: 1.125rem;
      width: 1.125rem;
      height: 1.125rem;
    }

    .estado-option {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 8px;
      border-radius: 8px;
      font-weight: 500;
    }

    .estado-option.programada {
      background-color: var(--warning-100);
      color: var(--warning-700);
    }

    .estado-option.confirmada {
      background-color: var(--success-100);
      color: var(--success-700);
    }

    .estado-option.en-proceso {
      background-color: var(--info-100);
      color: var(--info-700);
    }

    .estado-option.completada {
      background-color: var(--success-100);
      color: var(--success-700);
    }

    .estado-option.cancelada {
      background-color: var(--error-100);
      color: var(--error-700);
    }

    .estado-option.no-asistio {
      background-color: var(--gray-100);
      color: var(--gray-700);
    }

    .estado-option mat-icon {
      font-size: 1.125rem;
      width: 1.125rem;
      height: 1.125rem;
    }

    .dialog-actions {
      padding: 24px 0 0 0;
      border-top: 1px solid var(--border-light);
      display: flex;
      gap: 16px;
      justify-content: flex-end;
    }

    .cancel-button {
      padding: 12px 24px;
      border-radius: 12px;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    .cancel-button:hover {
      background-color: var(--gray-100);
    }

    .save-button {
      padding: 12px 32px;
      border-radius: 12px;
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .save-button:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .save-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
      .datetime-row {
        flex-direction: column;
        gap: 16px;
      }
      
      .half-width {
        width: 100%;
      }
      
      .dialog-actions {
        flex-direction: column-reverse;
      }
      
      .cancel-button,
      .save-button {
        width: 100%;
        justify-content: center;
      }
    }
  `]
})
export class CitaFormComponent implements OnInit {
  citaForm: FormGroup;
  isEdit: boolean = false;
  isLoading: boolean = false;
  isLoadingPacientes: boolean = true;
  pacientes: Paciente[] = [];
  minDate: Date = new Date();

  constructor(
    private fb: FormBuilder,
    private api: Api,
    public dialogRef: MatDialogRef<CitaFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CitaData
  ) {
    this.isEdit = !!data?.id;
    this.citaForm = this.createForm();
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
      fecha: ['', [Validators.required]],
      hora: ['', [Validators.required]],
      tipo_estudio: ['', [Validators.required]],
      estado: ['programada', [Validators.required]],
      observaciones: [''],
      estudio_id: [''],
      tecnico_asignado: [''],
      sala: [''],
      duracion_minutos: [30, [Validators.min(15), Validators.max(180)]]
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
    if (this.data.fecha_hora) {
      const fechaHora = new Date(this.data.fecha_hora);
      const fecha = new Date(fechaHora.getFullYear(), fechaHora.getMonth(), fechaHora.getDate());
      const hora = fechaHora.toTimeString().substring(0, 5);

      this.citaForm.patchValue({
        paciente_id: this.data.paciente_id,
        fecha: fecha,
        hora: hora,
        tipo_estudio: this.data.tipo_estudio,
        estado: this.data.estado,
        observaciones: this.data.observaciones || ''
      });
    }
  }

  onSave(): void {
    if (this.citaForm.valid) {
      this.isLoading = true;
      const formValue = { ...this.citaForm.value };

      // Combinar fecha y hora
      if (formValue.fecha && formValue.hora) {
        const fecha = new Date(formValue.fecha);
        const [hours, minutes] = formValue.hora.split(':');
        fecha.setHours(parseInt(hours), parseInt(minutes), 0, 0);

        formValue.fecha_cita = fecha.toISOString();
        delete formValue.fecha;
        delete formValue.hora;
      }

      // Validar que todos los campos requeridos estén presentes y no vacíos
      if (!formValue.paciente_id || formValue.paciente_id === '' || 
          !formValue.fecha_cita || formValue.fecha_cita === '' || 
          !formValue.tipo_estudio || formValue.tipo_estudio === '') {
        console.error('Campos requeridos faltantes o vacíos:', formValue);
        console.error('paciente_id:', formValue.paciente_id);
        console.error('fecha_cita:', formValue.fecha_cita);
        console.error('tipo_estudio:', formValue.tipo_estudio);
        this.isLoading = false;
        return;
      }

      // Log para debugging
      console.log('Datos enviados al backend:', formValue);

      // Realizar petición real al backend
      const operation = this.isEdit
        ? this.api.put(`api/citas/${this.data.id}`, formValue)
        : this.api.post('api/citas', formValue);

      operation.subscribe({
        next: (response) => {
          console.log('Respuesta del backend:', response);
          this.isLoading = false;
          this.dialogRef.close(response);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error completo al guardar cita:', error);
          console.error('Detalles del error:', error.error);
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
