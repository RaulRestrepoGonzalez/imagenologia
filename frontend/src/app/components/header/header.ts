import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    MatIconModule, 
    MatButtonModule, 
    MatMenuModule, 
    MatDividerModule
  ],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class Header {
  private notificacionesNoLeidas = 2; // Valor fijo para evitar NG0100
  
  getNotificacionesNoLeidas(): number {
    // Simular notificaciones no leídas para demostración
    return this.notificacionesNoLeidas;
  }

  markAllAsRead(): void {
    // Implementar lógica para marcar todas como leídas
    console.log('Marcando todas las notificaciones como leídas');
  }

  logout(): void {
    // Implementar lógica de cierre de sesión
    console.log('Cerrando sesión');
  }
}
