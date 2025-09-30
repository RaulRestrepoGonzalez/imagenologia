import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { SidebarService } from '../../services/sidebar.service';

@Component({
  selector: 'app-sidebar-toggle',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, MatTooltipModule],
  template: `
    <button
      mat-fab
      class="sidebar-toggle-btn"
      [class.collapsed]="sidebarService.isCollapsed()"
      (click)="toggleSidebar()"
      [attr.aria-label]="sidebarService.isCollapsed() ? 'Expandir menú' : 'Contraer menú'"
      [matTooltip]="sidebarService.isCollapsed() ? 'Expandir menú' : 'Contraer menú'"
      matTooltipPosition="right"
      matTooltipClass="orange-tooltip"
    >
      <mat-icon>{{ sidebarService.isCollapsed() ? 'menu_open' : 'menu' }}</mat-icon>
    </button>
  `,
  styles: [
    `
      .sidebar-toggle-btn {
        position: fixed;
        top: 20px;
        left: 300px;
        z-index: 1100;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        color: white;
        box-shadow:
          0 6px 20px rgba(255, 107, 53, 0.3),
          0 2px 6px rgba(255, 107, 53, 0.2);
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 56px;
        height: 56px;
        transform: scale(0.9);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.1);
      }

      .sidebar-toggle-btn:hover {
        background: linear-gradient(135deg, #ff5722, #e68900);
        box-shadow:
          0 8px 30px rgba(255, 87, 34, 0.4),
          0 4px 12px rgba(255, 107, 53, 0.3);
        transform: scale(1) translateY(-2px);
        border-color: rgba(255, 255, 255, 0.2);
      }

      .sidebar-toggle-btn:active {
        transform: scale(0.9) translateY(0px);
        box-shadow:
          0 4px 15px rgba(255, 107, 53, 0.4),
          0 2px 6px rgba(255, 107, 53, 0.2);
      }

      .sidebar-toggle-btn.collapsed {
        left: 100px;
        background: linear-gradient(135deg, #f7931e, #ff6b35);
        box-shadow:
          0 6px 20px rgba(247, 147, 30, 0.3),
          0 2px 6px rgba(247, 147, 30, 0.2);
      }

      .sidebar-toggle-btn.collapsed:hover {
        background: linear-gradient(135deg, #e68900, #ff5722);
        box-shadow:
          0 8px 30px rgba(230, 137, 0, 0.4),
          0 4px 12px rgba(247, 147, 30, 0.3);
        transform: scale(1) translateY(-2px);
      }

      .sidebar-toggle-btn mat-icon {
        font-size: 28px;
        width: 28px;
        height: 28px;
        transition: transform 0.3s ease;
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
      }

      .sidebar-toggle-btn:hover mat-icon {
        transform: scale(1.1) rotate(5deg);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
      }

      /* Responsive adjustments */
      @media (max-width: 1024px) {
        .sidebar-toggle-btn {
          left: 260px;
          width: 52px;
          height: 52px;
        }

        .sidebar-toggle-btn.collapsed {
          left: 90px;
        }
      }

      @media (max-width: 768px) {
        .sidebar-toggle-btn {
          left: 20px;
          top: 15px;
          width: 48px;
          height: 48px;
        }

        .sidebar-toggle-btn.collapsed {
          left: 20px;
        }

        .sidebar-toggle-btn mat-icon {
          font-size: 24px;
          width: 24px;
          height: 24px;
        }
      }

      /* Smooth animation when sidebar state changes */
      @media (min-width: 769px) {
        .sidebar-toggle-btn {
          transition:
            left 0.3s cubic-bezier(0.4, 0, 0.2, 1),
            background 0.3s ease,
            box-shadow 0.3s ease,
            transform 0.3s ease;
        }
      }

      /* Focus styles for accessibility */
      .sidebar-toggle-btn:focus {
        outline: 3px solid rgba(255, 255, 255, 0.4);
        outline-offset: 3px;
        box-shadow:
          0 8px 30px rgba(255, 107, 53, 0.5),
          0 0 0 3px rgba(255, 255, 255, 0.3);
      }

      /* Pulse animation for better visibility */
      .sidebar-toggle-btn::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(247, 147, 30, 0.2));
        transform: scale(0.8);
        opacity: 0;
        transition: all 0.3s ease;
        z-index: -1;
      }

      .sidebar-toggle-btn:hover::before {
        transform: scale(1.1);
        opacity: 1;
      }

      .sidebar-toggle-btn::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        transform: translate(-50%, -50%) scale(0);
        transition: transform 0.3s ease;
        z-index: 1;
      }

      .sidebar-toggle-btn:active::after {
        transform: translate(-50%, -50%) scale(3);
        opacity: 0;
      }

      /* Custom tooltip styles */
      :host ::ng-deep .orange-tooltip {
        background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
        color: white !important;
        font-size: 12px !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
      }

      :host ::ng-deep .orange-tooltip .mat-mdc-tooltip-trigger {
        background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
      }
    `,
  ],
})
export class SidebarToggle {
  constructor(public sidebarService: SidebarService) {}

  toggleSidebar() {
    this.sidebarService.toggle();
  }
}
