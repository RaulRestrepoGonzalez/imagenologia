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
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { Api } from '../../../services/api';

export interface InformeData {
  id?: number;
  estudio_id: number;
  paciente_id?: number;
  medico_radiologo: string;
  fecha_informe: string;
  hallazgos: string;
  impresion_diagnostica: string;
  recomendaciones?: string;
  estado: string;
  tecnica_utilizada?: string;
  calidad_estudio: string;
  urgente: boolean;
  validado: boolean;
  observaciones_tecnicas?: string;
  paciente_nombre?: string;
  estudio_tipo?: string;
}

export interface Estudio {
  id: number;
  paciente_id: number;
  paciente_nombre: string;
  paciente_apellidos?: string;
  paciente_cedula?: string;
  paciente_edad?: number;
  tipo_estudio: string;
  fecha_realizacion: string;
  modalidad: string;
  parte_cuerpo: string;
  estado: string;
  medico_solicitante?: string;
  observaciones?: string;
}

@Component({
  selector: 'app-informe-form',
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
    MatCheckboxModule,
    MatTabsModule,
    MatCardModule
  ],
  template: `
    <h2 mat-dialog-title>{{ isEdit ? 'Editar' : 'Crear' }} Informe Radiológico</h2>
    <mat-dialog-content>
      <form [formGroup]="informeForm" class="form-container">
        <mat-tab-group animationDuration="300ms">
          <!-- Información General -->
          <mat-tab label="Información General">
            <div class="tab-content">
              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Seleccionar Estudio</mat-label>
                <mat-select formControlName="estudio_id" [disabled]="isLoadingEstudios" (selectionChange)="onEstudioSelected($event.value)">
                  <mat-option *ngIf="isLoadingEstudios" disabled>
                    Cargando estudios...
                  </mat-option>
                  <mat-option *ngFor="let estudio of estudios" [value]="estudio.id">
                    <div class="estudio-option">
                      <div class="patient-info">
                        <strong>{{ estudio.paciente_nombre }} {{ estudio.paciente_apellidos }}</strong>
                        <span class="cedula" *ngIf="estudio.paciente_cedula">CC: {{ estudio.paciente_cedula }}</span>
                      </div>
                      <div class="study-info">
                        {{ estudio.tipo_estudio }} - {{ estudio.fecha_realizacion | date:'dd/MM/yyyy' }}
                        <span class="modalidad">({{ estudio.modalidad }})</span>
                      </div>
                    </div>
                  </mat-option>
                </mat-select>
                <mat-error *ngIf="informeForm.get('estudio_id')?.hasError('required')">
                  Seleccione un estudio
                </mat-error>
              </mat-form-field>

              <!-- Información del Paciente y Estudio Seleccionado -->
              <div *ngIf="selectedEstudio" class="patient-study-info">
                <mat-card class="info-card">
                  <mat-card-header>
                    <mat-card-title>Información del Paciente y Estudio</mat-card-title>
                  </mat-card-header>
                  <mat-card-content>
                    <div class="info-grid">
                      <div class="info-section">
                        <h4>Datos del Paciente</h4>
                        <p><strong>Nombre:</strong> {{ selectedEstudio.paciente_nombre }} {{ selectedEstudio.paciente_apellidos }}</p>
                        <p *ngIf="selectedEstudio.paciente_cedula"><strong>Cédula:</strong> {{ selectedEstudio.paciente_cedula }}</p>
                        <p *ngIf="selectedEstudio.paciente_edad"><strong>Edad:</strong> {{ selectedEstudio.paciente_edad }} años</p>
                      </div>
                      <div class="info-section">
                        <h4>Datos del Estudio</h4>
                        <p><strong>Tipo:</strong> {{ selectedEstudio.tipo_estudio }}</p>
                        <p><strong>Modalidad:</strong> {{ selectedEstudio.modalidad }}</p>
                        <p><strong>Fecha:</strong> {{ selectedEstudio.fecha_realizacion | date:'dd/MM/yyyy HH:mm' }}</p>
                        <p><strong>Estado:</strong> {{ selectedEstudio.estado }}</p>
                        <p *ngIf="selectedEstudio.medico_solicitante"><strong>Médico Solicitante:</strong> {{ selectedEstudio.medico_solicitante }}</p>
                      </div>
                    </div>
                    <div *ngIf="selectedEstudio.observaciones" class="observations">
                      <h4>Observaciones del Estudio</h4>
                      <p>{{ selectedEstudio.observaciones }}</p>
                    </div>
                  </mat-card-content>
                </mat-card>
              </div>

              <div class="row">
                <mat-form-field appearance="fill" class="half-width">
                  <mat-label>Médico Radiólogo</mat-label>
                  <input matInput formControlName="medico_radiologo"
                         placeholder="Dr(a). Nombre del radiólogo">
                  <mat-error *ngIf="informeForm.get('medico_radiologo')?.hasError('required')">
                    El radiólogo es requerido
                  </mat-error>
                </mat-form-field>

                <mat-form-field appearance="fill" class="half-width">
                  <mat-label>Fecha del Informe</mat-label>
                  <input matInput [matDatepicker]="picker" formControlName="fecha_informe">
                  <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
                  <mat-datepicker #picker></mat-datepicker>
                  <mat-error *ngIf="informeForm.get('fecha_informe')?.hasError('required')">
                    La fecha es requerida
                  </mat-error>
                </mat-form-field>
              </div>

              <div class="row">
                <mat-form-field appearance="fill" class="half-width">
                  <mat-label>Estado del Informe</mat-label>
                  <mat-select formControlName="estado">
                    <mat-option value="Borrador">Borrador</mat-option>
                    <mat-option value="En Revisión">En Revisión</mat-option>
                    <mat-option value="Completado">Completado</mat-option>
                    <mat-option value="Validado">Validado</mat-option>
                    <mat-option value="Entregado">Entregado</mat-option>
                    <mat-option value="Corregido">Corregido</mat-option>
                  </mat-select>
                  <mat-error *ngIf="informeForm.get('estado')?.hasError('required')">
                    Seleccione un estado
                  </mat-error>
                </mat-form-field>

                <mat-form-field appearance="fill" class="half-width">
                  <mat-label>Calidad del Estudio</mat-label>
                  <mat-select formControlName="calidad_estudio">
                    <mat-option value="Excelente">Excelente</mat-option>
                    <mat-option value="Buena">Buena</mat-option>
                    <mat-option value="Regular">Regular</mat-option>
                    <mat-option value="Deficiente">Deficiente</mat-option>
                  </mat-select>
                  <mat-error *ngIf="informeForm.get('calidad_estudio')?.hasError('required')">
                    Seleccione la calidad
                  </mat-error>
                </mat-form-field>
              </div>

              <div class="checkboxes-row">
                <mat-checkbox formControlName="urgente">
                  <span class="checkbox-label">Informe urgente</span>
                </mat-checkbox>

                <mat-checkbox formControlName="validado">
                  <span class="checkbox-label">Informe validado</span>
                </mat-checkbox>
              </div>
            </div>
          </mat-tab>

          <!-- Contenido Médico -->
          <mat-tab label="Contenido Médico">
            <div class="tab-content">
              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Técnica Utilizada</mat-label>
                <textarea matInput formControlName="tecnica_utilizada" rows="3"
                          placeholder="Describa la técnica utilizada para el estudio...">
                </textarea>
              </mat-form-field>

              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Hallazgos</mat-label>
                <textarea matInput formControlName="hallazgos" rows="6"
                          placeholder="Describa los hallazgos encontrados en el estudio...">
                </textarea>
                <mat-error *ngIf="informeForm.get('hallazgos')?.hasError('required')">
                  Los hallazgos son requeridos
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Impresión Diagnóstica</mat-label>
                <textarea matInput formControlName="impresion_diagnostica" rows="4"
                          placeholder="Escriba la impresión diagnóstica...">
                </textarea>
                <mat-error *ngIf="informeForm.get('impresion_diagnostica')?.hasError('required')">
                  La impresión diagnóstica es requerida
                </mat-error>
              </mat-form-field>

              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Recomendaciones</mat-label>
                <textarea matInput formControlName="recomendaciones" rows="3"
                          placeholder="Escriba las recomendaciones (opcional)...">
                </textarea>
              </mat-form-field>
            </div>
          </mat-tab>

          <!-- Observaciones Técnicas -->
          <mat-tab label="Observaciones">
            <div class="tab-content">
              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Observaciones Técnicas</mat-label>
                <textarea matInput formControlName="observaciones_tecnicas" rows="8"
                          placeholder="Ingrese observaciones técnicas adicionales (opcional)...">
                </textarea>
              </mat-form-field>

              <div class="info-section">
                <mat-icon>info</mat-icon>
                <div class="info-content">
                  <h4>Información Adicional</h4>
                  <p>Las observaciones técnicas pueden incluir:</p>
                  <ul>
                    <li>Limitaciones del estudio</li>
                    <li>Artefactos presentes</li>
                    <li>Calidad de las imágenes</li>
                    <li>Consideraciones especiales</li>
                    <li>Correlación con estudios previos</li>
                  </ul>
                </div>
              </div>
            </div>
          </mat-tab>
        </mat-tab-group>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="onSave()"
              [disabled]="isLoading">
        {{ isLoading ? 'Guardando...' : 'Guardar' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .form-container {
      padding: 1rem 0;
      max-width: 800px;
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
      margin-bottom: 1rem;
      align-items: center;
    }

    .checkbox-label {
      font-size: 0.95rem;
      color: #333;
      margin-left: 0.5rem;
    }

    .tab-content {
      padding: 1rem 0;
    }

    .info-section {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      margin: 1rem 0;
      padding: 1rem;
      background-color: #f5f5f5;
      border-radius: 8px;
      border-left: 4px solid #2196f3;

      mat-icon {
        color: #2196f3;
        margin-top: 0.25rem;
      }

      .info-content {
        flex: 1;

        h4 {
          margin: 0 0 0.5rem 0;
          color: #333;
          font-size: 1rem;
        }

        p {
          margin: 0 0 0.5rem 0;
          color: #666;
          font-size: 0.9rem;
        }

        ul {
          margin: 0;
          padding-left: 1.5rem;
          color: #666;
          font-size: 0.9rem;

          li {
            margin-bottom: 0.25rem;
          }
        }
      }
    }

    mat-dialog-content {
      max-height: 80vh;
      overflow-y: auto;
    }

    mat-dialog-actions {
      padding: 1rem 0;
    }

    textarea {
      resize: vertical;
      min-height: 60px;
    }

    mat-checkbox {
      display: flex;
      align-items: center;
    }

    ::ng-deep .mat-mdc-tab-group {
      .mat-mdc-tab-header {
        border-bottom: 1px solid #e0e0e0;
      }

      .mat-mdc-tab-body-wrapper {
        margin-top: 0;
      }
    }

    @media (max-width: 600px) {
      .row {
        flex-direction: column;
      }

      .checkboxes-row {
        flex-direction: column;
        gap: 1rem;
      }

      .info-section {
        flex-direction: column;
      }
    }
  `]
})
export class InformeFormComponent implements OnInit {
  informeForm: FormGroup;
  isEdit: boolean = false;
  isLoading: boolean = false;
  isLoadingEstudios: boolean = true;
  estudios: Estudio[] = [];
  selectedEstudio: Estudio | null = null;

  constructor(
    private fb: FormBuilder,
    private api: Api,
    public dialogRef: MatDialogRef<InformeFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: InformeData
  ) {
    this.isEdit = !!data?.id;
    this.informeForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadEstudios();
    if (this.isEdit && this.data) {
      this.populateForm();
    }
  }

  loadEstudios(): void {
    this.isLoadingEstudios = true;
    this.api.get('api/estudios').subscribe({
      next: (response: any[]) => {
        this.estudios = response.map(e => ({
          id: e.id,
          paciente_id: e.paciente_id,
          paciente_nombre: e.paciente_nombre || 'Paciente no encontrado',
          paciente_apellidos: e.paciente_apellidos || '',
          paciente_cedula: e.paciente_cedula,
          paciente_edad: e.paciente_edad,
          tipo_estudio: e.tipo_estudio,
          fecha_realizacion: e.fecha_realizacion,
          modalidad: e.modalidad || 'No especificada',
          parte_cuerpo: e.parte_cuerpo || 'No especificada',
          estado: e.estado,
          medico_solicitante: e.medico_solicitante,
          observaciones: e.observaciones
        }));
        this.isLoadingEstudios = false;
        
        // Set selected estudio if editing
        if (this.isEdit && this.data?.estudio_id) {
          this.selectedEstudio = this.estudios.find(e => e.id === this.data.estudio_id) || null;
        }
      },
      error: (error) => {
        console.error('Error al cargar estudios:', error);
        this.isLoadingEstudios = false;
      }
    });
  }

  onEstudioSelected(estudioId: number): void {
    this.selectedEstudio = this.estudios.find(e => e.id === estudioId) || null;
    if (this.selectedEstudio) {
      console.log('Estudio seleccionado:', this.selectedEstudio);
      // Auto-completar algunos campos basados en el estudio
      this.informeForm.patchValue({
        paciente_id: this.selectedEstudio.paciente_id
      });
    }
  }

  private createForm(): FormGroup {
    return this.fb.group({
      estudio_id: ['', [Validators.required]],
      medico_radiologo: ['', [Validators.required]],
      fecha_informe: [new Date(), [Validators.required]],
      hallazgos: ['', [Validators.required, Validators.minLength(10)]],
      impresion_diagnostica: ['', [Validators.required, Validators.minLength(5)]],
      recomendaciones: [''],
      estado: ['Borrador', [Validators.required]],
      tecnica_utilizada: [''],
      calidad_estudio: ['Buena', [Validators.required]],
      urgente: [false],
      validado: [false],
      observaciones_tecnicas: ['']
    });
  }

  private populateForm(): void {
    if (this.data) {
      const fecha = new Date(this.data.fecha_informe);
      this.informeForm.patchValue({
        estudio_id: this.data.estudio_id,
        medico_radiologo: this.data.medico_radiologo,
        fecha_informe: fecha,
        hallazgos: this.data.hallazgos,
        impresion_diagnostica: this.data.impresion_diagnostica,
        recomendaciones: this.data.recomendaciones || '',
        estado: this.data.estado,
        tecnica_utilizada: this.data.tecnica_utilizada || '',
        calidad_estudio: this.data.calidad_estudio,
        urgente: this.data.urgente || false,
        validado: this.data.validado || false,
        observaciones_tecnicas: this.data.observaciones_tecnicas || ''
      });
      
      // Set selected estudio if editing
      if (this.data.estudio_id) {
        this.selectedEstudio = this.estudios.find(e => e.id === this.data.estudio_id) || null;
      }
    }
  }

  onSave(): void {
    console.log('onSave called - Form valid:', this.informeForm.valid);
    console.log('Form value:', this.informeForm.value);
    console.log('Form errors:', this.getFormErrors());
    
    if (this.isLoading) {
      console.log('Ya está guardando, ignorando click');
      return;
    }
    
    this.isLoading = true;
    const formValue = { ...this.informeForm.value };

    // Validar campos requeridos manualmente
    if (!formValue.estudio_id || !formValue.medico_radiologo || !formValue.hallazgos || !formValue.impresion_diagnostica) {
      console.error('Campos requeridos faltantes:', formValue);
      alert('Por favor complete todos los campos requeridos: Estudio, Médico Radiólogo, Hallazgos e Impresión Diagnóstica');
      this.isLoading = false;
      return;
    }

    // Formatear fecha
    if (formValue.fecha_informe instanceof Date) {
      formValue.fecha_informe = formValue.fecha_informe.toISOString();
    }

    console.log('Datos enviados al backend (informe):', formValue);

    const operation = this.isEdit
      ? this.api.put(`api/informes/${this.data.id}`, formValue)
      : this.api.post('api/informes', formValue);

    operation.subscribe({
      next: (response) => {
        console.log('Respuesta del backend (informe):', response);
        this.isLoading = false;
        this.dialogRef.close(response);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error completo al guardar informe:', error);
        console.error('Detalles del error:', error.error);
        alert(`Error al guardar: ${error.error?.detail || error.message || 'Error desconocido'}`);
      }
    });
  }

  private getFormErrors(): any {
    const errors: any = {};
    Object.keys(this.informeForm.controls).forEach(key => {
      const control = this.informeForm.get(key);
      if (control && control.errors) {
        errors[key] = control.errors;
      }
    });
    return errors;
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
