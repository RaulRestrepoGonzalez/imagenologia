import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-unauthorized',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="unauthorized-container">
      <mat-card class="unauthorized-card">
        <mat-card-content>
          <div class="unauthorized-icon">
            <mat-icon>block</mat-icon>
          </div>
          <h2>Acceso No Autorizado</h2>
          <p>No tienes permisos para acceder a esta página.</p>
          <div class="actions">
            <button mat-raised-button color="primary" (click)="goHome()">
              Ir al Inicio
            </button>
            <button mat-button (click)="logout()">
              Cerrar Sesión
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .unauthorized-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #f5f5f5;
    }

    .unauthorized-card {
      max-width: 400px;
      text-align: center;
      padding: 2rem;
    }

    .unauthorized-icon {
      font-size: 4rem;
      color: #f44336;
      margin-bottom: 1rem;
    }

    .unauthorized-icon mat-icon {
      font-size: 4rem;
      width: 4rem;
      height: 4rem;
    }

    h2 {
      color: #333;
      margin-bottom: 1rem;
    }

    p {
      color: #666;
      margin-bottom: 2rem;
    }

    .actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
    }
  `]
})
export class UnauthorizedComponent {
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  goHome(): void {
    this.router.navigate(['/']);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
