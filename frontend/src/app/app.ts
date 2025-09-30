import { Component, signal, computed } from '@angular/core';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterOutlet } from '@angular/router';
import { Header } from './components/header/header';
import { Sidebar } from './components/sidebar/sidebar';
import { SidebarToggle } from './components/sidebar-toggle/sidebar-toggle';
import { Footer } from './components/footer/footer';
import { SidebarService } from './services/sidebar.service';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.html',
  styleUrl: './app.scss',
  imports: [
    RouterOutlet,
    Header,
    Sidebar,
    SidebarToggle,
    Footer,
    MatMenuModule,
    MatIconModule,
    MatToolbarModule,
  ],
})
export class App {
  protected readonly title = signal('Sistema Clínico');

  isCollapsed = computed(() => this.sidebarService.isCollapsed());

  constructor(private sidebarService: SidebarService) {}
}
