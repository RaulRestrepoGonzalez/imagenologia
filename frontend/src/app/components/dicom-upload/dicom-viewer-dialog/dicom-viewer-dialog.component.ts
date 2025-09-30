import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-dicom-viewer-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <h2 mat-dialog-title>Visualizador DICOM</h2>
    
    <mat-dialog-content class="dicom-viewer-content">
      <div class="viewer-container" *ngIf="!isLoading; else loading">
        <div class="toolbar">
          <button mat-icon-button (click)="adjustContrast(-0.1)" title="Disminuir contraste">
            <mat-icon>contrast</mat-icon>
          </button>
          <button mat-icon-button (click)="adjustContrast(0.1)" title="Aumentar contraste">
            <mat-icon>contrast</mat-icon>
          </button>
          <button mat-icon-button (click)="zoomIn()" title="Acercar">
            <mat-icon>zoom_in</mat-icon>
          </button>
          <button mat-icon-button (click)="zoomOut()" title="Alejar">
            <mat-icon>zoom_out</mat-icon>
          </button>
          <button mat-icon-button (click)="rotate(90)" title="Rotar 90°">
            <mat-icon>rotate_90_degrees_ccw</mat-icon>
          </button>
          <span class="spacer"></span>
          <button mat-icon-button (click)="downloadDicom()" title="Descargar DICOM">
            <mat-icon>download</mat-icon>
          </button>
        </div>
        
        <div class="image-container">
          <img 
            #dicomImage 
            [src]="imageUrl" 
            [style.transform]="'scale(' + zoomLevel + ') rotate(' + rotation + 'deg)'"
            [style.filter]="'contrast(' + (1 + contrastLevel) + ')'"
            (load)="onImageLoad()"
            alt="DICOM Image"
            class="dicom-image"
          >
        </div>
        
        <div class="metadata" *ngIf="metadata">
          <h3>Metadatos DICOM</h3>
          <div class="metadata-grid">
            <div class="metadata-item" *ngFor="let item of metadata | keyvalue">
              <strong>{{item.key}}:</strong> {{item.value}}
            </div>
          </div>
        </div>
      </div>
      
      <ng-template #loading>
        <div class="loading-container">
          <mat-spinner></mat-spinner>
          <p>Cargando imagen DICOM...</p>
        </div>
      </ng-template>
    </mat-dialog-content>
    
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .dicom-viewer-content {
      max-width: 90vw;
      max-height: 80vh;
      overflow: auto;
    }
    
    .viewer-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .toolbar {
      display: flex;
      gap: 0.5rem;
      padding: 0.5rem;
      background: #f5f5f5;
      border-radius: 4px;
    }
    
    .spacer {
      flex: 1;
    }
    
    .image-container {
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: auto;
      background-color: #000;
      min-height: 400px;
      max-height: 60vh;
    }
    
    .dicom-image {
      max-width: 100%;
      max-height: 60vh;
      object-fit: contain;
      transition: transform 0.3s ease, filter 0.3s ease;
    }
    
    .metadata {
      margin-top: 1rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 4px;
    }
    
    .metadata-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 0.5rem;
      margin-top: 0.5rem;
    }
    
    .metadata-item {
      padding: 0.25rem 0;
      font-size: 0.9em;
    }
    
    .loading-container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 400px;
      gap: 1rem;
    }
  `]
})
export class DicomViewerDialogComponent implements OnInit {
  imageUrl: string = '';
  isLoading: boolean = true;
  zoomLevel: number = 1;
  rotation: number = 0;
  contrastLevel: number = 0;
  metadata: any = null;

  constructor(
    public dialogRef: MatDialogRef<DicomViewerDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadDicomImage();
  }

  loadDicomImage(): void {
    this.isLoading = true;
    const { estudioId, file } = this.data;
    
    // Load the preview image
    this.imageUrl = `${environment.apiUrl}/api/dicom/preview/${estudioId}/${file.preview_name}`;
    
    // In a real app, you would fetch the DICOM metadata here
    // For now, we'll just show some basic file info
    this.metadata = {
      'Nombre del archivo': file.original_name,
      'Tamaño': this.formatFileSize(file.size),
      'Subido el': new Date(file.uploaded_at).toLocaleString(),
      'Tipo de estudio': 'DICOM',
      'Resolución': '512x512', // This would come from DICOM metadata
      'Profundidad de bits': '16 bits' // This would come from DICOM metadata
    };
  }

  onImageLoad(): void {
    this.isLoading = false;
  }

  zoomIn(): void {
    this.zoomLevel = Math.min(this.zoomLevel + 0.2, 3);
  }

  zoomOut(): void {
    this.zoomLevel = Math.max(this.zoomLevel - 0.2, 0.5);
  }

  rotate(degrees: number): void {
    this.rotation = (this.rotation + degrees) % 360;
  }

  adjustContrast(amount: number): void {
    this.contrastLevel = Math.max(-0.9, Math.min(0.9, this.contrastLevel + amount));
  }

  downloadDicom(): void {
    const { estudioId, file } = this.data;
    const url = `${environment.apiUrl}/api/dicom/download/${estudioId}/${file.saved_name}`;
    window.open(url, '_blank');
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
