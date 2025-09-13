import { Routes } from '@angular/router';
import { Estudios } from './components/estudios/estudios';
import { Informes } from './components/informes/informes';
import { Pacientes } from './components/pacientes/pacientes';
import { Citas } from './components/citas/citas';
import { Notificaciones } from './components/notificaciones/notificaciones';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./components/login/login').then((m) => m.LoginComponent),
    title: 'Iniciar Sesión'
  },
  {
    path: 'unauthorized',
    loadComponent: () => import('./components/unauthorized/unauthorized.component').then((m) => m.UnauthorizedComponent),
    title: 'Acceso No Autorizado'
  },
  {
    path: 'estudios',
    component: Estudios,
    title: 'Estudios',
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'radiologo', 'secretario'] }
  },
  {
    path: 'informes',
    component: Informes,
    title: 'Informes',
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'radiologo'] }
  },
  {
    path: 'pacientes',
    component: Pacientes,
    title: 'Pacientes',
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'radiologo', 'secretario'] }
  },
  {
    path: 'citas',
    component: Citas,
    title: 'Citas',
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'radiologo', 'secretario'] }
  },
  {
    path: 'notificaciones',
    component: Notificaciones,
    title: 'Notificaciones',
    canActivate: [AuthGuard]
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    title: 'Dashboard',
    canActivate: [AuthGuard]
  },
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];
