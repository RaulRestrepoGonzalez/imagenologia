import { Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth.service';
import { SidebarService } from '../../services/sidebar.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  private notificacionesNoLeidas = 3; // Valor fijo para evitar NG0100

  isCollapsed = computed(() => this.sidebarService.isCollapsed());

  constructor(
    private authService: AuthService,
    private sidebarService: SidebarService,
  ) {}

  getNotificacionesNoLeidas(): number {
    // Simular notificaciones no leídas para demostración
    return this.notificacionesNoLeidas;
  }

  logout(): void {
    // Implementar lógica de cierre de sesión
    console.log('Cerrando sesión desde sidebar');
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isTechnician(): boolean {
    return this.authService.isTechnician();
  }
}
