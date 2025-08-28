import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {
  
  getNotificacionesNoLeidas(): number {
    // Simular notificaciones no leídas para demostración
    return Math.floor(Math.random() * 5) + 1;
  }

  logout(): void {
    // Implementar lógica de cierre de sesión
    console.log('Cerrando sesión desde sidebar');
  }
}
