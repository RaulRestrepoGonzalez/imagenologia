import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="dashboard-container">
      <div class="welcome-section">
        <h1>Bienvenido, {{currentUser?.nombre}} {{currentUser?.apellidos}}</h1>
        <p class="role-badge">{{getRoleLabel(currentUser?.role)}}</p>
      </div>

      <div class="dashboard-grid">
        <!-- Admin Dashboard -->
        <div *ngIf="authService.isAdmin()" class="admin-section">
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar>admin_panel_settings</mat-icon>
              <mat-card-title>Panel de Administración</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <p>Gestiona usuarios, configuraciones y reportes del sistema.</p>
            </mat-card-content>
            <mat-card-actions>
              <button mat-raised-button color="primary" (click)="navigateTo('/pacientes')">
                Gestionar Pacientes
              </button>
              <button mat-raised-button color="accent" (click)="navigateTo('/citas')">
                Ver Citas
              </button>
            </mat-card-actions>
          </mat-card>
        </div>

        <!-- Medical Staff Dashboard -->
        <div *ngIf="authService.isMedicalStaff()" class="medical-section">
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar>medical_services</mat-icon>
              <mat-card-title>Panel Médico</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <p>Accede a estudios, informes y gestión de pacientes.</p>
            </mat-card-content>
            <mat-card-actions>
              <button mat-raised-button color="primary" (click)="navigateTo('/estudios')">
                Ver Estudios
              </button>
              <button mat-raised-button color="accent" (click)="navigateTo('/informes')">
                Generar Informes
              </button>
            </mat-card-actions>
          </mat-card>
        </div>

        <!-- Staff Dashboard -->
        <div *ngIf="authService.isStaff()" class="staff-section">
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar>people</mat-icon>
              <mat-card-title>Panel de Secretaría</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <p>Gestiona pacientes, citas y notificaciones.</p>
            </mat-card-content>
            <mat-card-actions>
              <button mat-raised-button color="primary" (click)="navigateTo('/pacientes')">
                Gestionar Pacientes
              </button>
              <button mat-raised-button color="accent" (click)="navigateTo('/citas')">
                Programar Citas
              </button>
            </mat-card-actions>
          </mat-card>
        </div>

        <!-- Patient Dashboard -->
        <div *ngIf="authService.isPatient()" class="patient-section">
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar>person</mat-icon>
              <mat-card-title>Mi Portal de Paciente</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <p>Consulta tus citas, estudios y notificaciones.</p>
            </mat-card-content>
            <mat-card-actions>
              <button mat-raised-button color="primary" (click)="navigateTo('/notificaciones')">
                Mis Notificaciones
              </button>
            </mat-card-actions>
          </mat-card>
        </div>

        <!-- Quick Actions -->
        <mat-card class="dashboard-card quick-actions">
          <mat-card-header>
            <mat-icon mat-card-avatar>flash_on</mat-icon>
            <mat-card-title>Acciones Rápidas</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="quick-buttons">
              <button mat-stroked-button (click)="navigateTo('/notificaciones')">
                <mat-icon>notifications</mat-icon>
                Notificaciones
              </button>
              <button mat-stroked-button (click)="logout()">
                <mat-icon>logout</mat-icon>
                Cerrar Sesión
              </button>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .welcome-section {
      text-align: center;
      margin-bottom: 2rem;
    }

    .welcome-section h1 {
      color: #333;
      margin-bottom: 0.5rem;
    }

    .role-badge {
      display: inline-block;
      background: #e3f2fd;
      color: #1976d2;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-weight: 500;
      text-transform: uppercase;
      font-size: 0.875rem;
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .dashboard-card {
      height: fit-content;
    }

    .dashboard-card mat-card-header {
      margin-bottom: 1rem;
    }

    .dashboard-card mat-card-actions {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .quick-actions .quick-buttons {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .quick-buttons button {
      justify-content: flex-start;
    }

    .quick-buttons mat-icon {
      margin-right: 0.5rem;
    }

    @media (max-width: 768px) {
      .dashboard-container {
        padding: 1rem;
      }

      .dashboard-grid {
        grid-template-columns: 1fr;
      }

      .dashboard-card mat-card-actions {
        flex-direction: column;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;

  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getUser();
  }

  getRoleLabel(role?: string): string {
    const roleLabels: { [key: string]: string } = {
      'admin': 'Administrador',
      'radiologo': 'Radiólogo',
      'secretario': 'Secretario',
      'paciente': 'Paciente'
    };
    return role ? roleLabels[role] || role : '';
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
