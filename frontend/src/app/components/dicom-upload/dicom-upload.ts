import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpEventType, HttpErrorResponse } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatListModule } from '@angular/material/list';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDividerModule } from '@angular/material/divider';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth.service';
import { DicomViewerDialogComponent } from './dicom-viewer-dialog/dicom-viewer-dialog.component';

interface Paciente {
  id: string;
  nombre: string;
  apellidos: string;
  identificacion: string;
  estudios_pendientes: number;
}

interface Estudio {
  id: string;
  paciente_id: string;
  paciente_nombre: string;
  paciente_apellidos: string;
  paciente_cedula: string;
  tipo_estudio: string;
  estado: string;
  fecha_solicitud: string;
  fecha_programada?: string;
  prioridad?: string;
  indicaciones?: string;
}

interface DicomFile {
  original_name: string;
  saved_name: string;
  preview_name: string;
  size: number;
  uploaded_at: string;
}

@Component({
  selector: 'app-dicom-upload',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatProgressBarModule,
    MatSnackBarModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    MatSelectModule,
    MatTableModule,
    MatDialogModule,
    MatChipsModule,
    MatTooltipModule,
    MatListModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatDividerModule,
    FormsModule
  ],
  templateUrl: './dicom-upload.component.html',
  styleUrls: ['./dicom-upload.component.scss']
})
export class DicomUploadComponent implements OnInit {
  selectedFiles: File[] = [];
  uploadProgress: number | null = null;
  isUploading = false;
  pacientes: Paciente[] = [];
  selectedPaciente: string = '';
  estudios: Estudio[] = [];
  selectedEstudio: string = '';
  selectedEstudioInfo: Estudio | null = null;
  displayedColumns: string[] = ['preview', 'name', 'size', 'date', 'actions'];
  dicomFiles: DicomFile[] = [];
  isLoading = false;
  isDragging = false;
  environment = environment;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadPacientes();
  }

  loadPacientes(): void {
    this.isLoading = true;
    this.http.get<Paciente[]>(`${environment.apiUrl}/api/dicom/pacientes-con-estudios`).subscribe({
      next: (data) => {
        this.pacientes = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading pacientes:', error);
        this.snackBar.open('Error al cargar los pacientes', 'Cerrar', {
          duration: 5000
        });
        this.isLoading = false;
      }
    });
  }

  onPacienteSelected(): void {
    if (!this.selectedPaciente) {
      this.estudios = [];
      this.selectedEstudio = '';
      this.selectedEstudioInfo = null;
      return;
    }

    this.isLoading = true;
    this.http.get<any>(`${environment.apiUrl}/api/dicom/estudios-por-paciente/${this.selectedPaciente}`).subscribe({
      next: (data) => {
        this.estudios = data.estudios;
        this.isLoading = false;
        
        // Auto-select first study if only one
        if (this.estudios.length === 1) {
          this.selectedEstudio = this.estudios[0].id;
          this.onEstudioSelected();
        }
      },
      error: (error) => {
        console.error('Error loading estudios:', error);
        this.snackBar.open('Error al cargar los estudios del paciente', 'Cerrar', {
          duration: 5000
        });
        this.isLoading = false;
      }
    });
  }

  onFileSelected(event: any): void {
    const files: FileList = event.target.files;
    if (files.length > 0) {
      this.selectedFiles = Array.from(files);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    // Optional: Add visual feedback for drag over
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer?.files) {
      const files = Array.from(event.dataTransfer.files);
      // Filter for DICOM files (.dcm)
      const dicomFiles = files.filter(file => file.name.toLowerCase().endsWith('.dcm'));
      
      if (dicomFiles.length > 0) {
        this.selectedFiles = [...this.selectedFiles, ...dicomFiles];
      } else {
        this.snackBar.open('Por favor, seleccione archivos DICOM (.dcm)', 'Cerrar', {
          duration: 5000
        });
      }
    }
  }

  removeFile(index: number): void {
    this.selectedFiles.splice(index, 1);
  }


  loadDicomFiles(estudioId: string): void {
    if (!estudioId) return;
    
    this.isLoading = true;
    this.http.get<any>(`${environment.apiUrl}/api/dicom/study/${estudioId}`).subscribe({
      next: (data) => {
        this.dicomFiles = data.archivos || [];
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading DICOM files:', error);
        this.snackBar.open('Error al cargar los archivos DICOM', 'Cerrar', {
          duration: 5000
        });
        this.isLoading = false;
      }
    });
  }

  onEstudioSelected(): void {
    // Find selected study info
    this.selectedEstudioInfo = this.estudios.find(e => e.id === this.selectedEstudio) || null;
    this.loadDicomFiles(this.selectedEstudio);
  }

  uploadFiles(): void {
    if (!this.selectedEstudio || this.selectedFiles.length === 0) {
      this.snackBar.open('Por favor seleccione un estudio y al menos un archivo', 'Cerrar', {
        duration: 5000
      });
      return;
    }

    this.isUploading = true;
    this.uploadProgress = 0;

    const formData = new FormData();
    this.selectedFiles.forEach(file => {
      formData.append('files', file, file.name);
    });

    this.http.post(`${environment.apiUrl}/api/dicom/upload/${this.selectedEstudio}`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event: any) => {
        if (event.type === HttpEventType.UploadProgress) {
          if (event.total) {
            this.uploadProgress = Math.round(100 * event.loaded / event.total);
          }
        } else if (event.type === HttpEventType.Response) {
          this.uploadProgress = null;
          this.isUploading = false;
          this.selectedFiles = [];
          this.loadDicomFiles(this.selectedEstudio);
          
          const response = event.body as any;
          const pacienteInfo = response.paciente;
          const imagenesAnexadas = response.imagenes_anexadas_a_informe || 0;
          
          this.snackBar.open(
            `✓ Archivos subidos para ${pacienteInfo?.nombre} ${pacienteInfo?.apellidos}. ${imagenesAnexadas} imágenes anexadas al informe.`,
            'Cerrar',
            {
              duration: 7000,
              panelClass: ['success-snackbar']
            }
          );
        }
      },
      error: (error: HttpErrorResponse) => {
        console.error('Upload error:', error);
        this.uploadProgress = null;
        this.isUploading = false;
        this.snackBar.open(`Error al subir archivos: ${error.error?.message || 'Error desconocido'}`, 'Cerrar', {
          duration: 10000
        });
      }
    });
  }

  viewDicom(estudioId: string, file: DicomFile): void {
    this.dialog.open(DicomViewerDialogComponent, {
      width: '90%',
      height: '90%',
      data: {
        estudioId,
        file
      },
      panelClass: 'dicom-viewer-dialog'
    });
  }

  downloadDicom(estudioId: string, fileName: string): void {
    const url = `${environment.apiUrl}/api/dicom/download/${estudioId}/${fileName}`;
    window.open(url, '_blank');
  }

  deleteDicom(estudioId: string, fileName: string): void {
    // TODO: Implement delete functionality
    this.snackBar.open('Funcionalidad de eliminación no implementada', 'Cerrar', {
      duration: 5000
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getPacienteDisplay(paciente: Paciente): string {
    return `${paciente.nombre} ${paciente.apellidos} - ${paciente.identificacion} (${paciente.estudios_pendientes} estudio${paciente.estudios_pendientes !== 1 ? 's' : ''})`;
  }

  getEstudioDisplay(estudio: Estudio): string {
    const fecha = estudio.fecha_programada || estudio.fecha_solicitud;
    return `${estudio.tipo_estudio} - ${new Date(fecha).toLocaleDateString()} (${estudio.estado})`;
  }

  getEstadoColor(estado: string): 'primary' | 'accent' | 'warn' {
    switch (estado?.toLowerCase()) {
      case 'completado':
        return 'primary';
      case 'en_proceso':
        return 'accent';
      case 'pendiente':
        return 'warn';
      default:
        return 'primary';
    }
  }
}
