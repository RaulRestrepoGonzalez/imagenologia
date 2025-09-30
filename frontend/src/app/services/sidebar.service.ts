import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SidebarService {
  private _isCollapsed = signal(false);

  constructor() {
    // Cargar estado del localStorage si existe
    const savedState = localStorage.getItem('sidebar-collapsed');
    if (savedState) {
      this._isCollapsed.set(JSON.parse(savedState));
    }
  }

  get isCollapsed() {
    return this._isCollapsed.asReadonly();
  }

  toggle() {
    const newState = !this._isCollapsed();
    this._isCollapsed.set(newState);
    // Guardar estado en localStorage
    localStorage.setItem('sidebar-collapsed', JSON.stringify(newState));
  }

  collapse() {
    this._isCollapsed.set(true);
    localStorage.setItem('sidebar-collapsed', JSON.stringify(true));
  }

  expand() {
    this._isCollapsed.set(false);
    localStorage.setItem('sidebar-collapsed', JSON.stringify(false));
  }
}
