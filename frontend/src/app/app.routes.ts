import { Routes } from '@angular/router';
import { Estudios } from './components/estudios/estudios';
import { Informes } from './components/informes/informes';
import { Pacientes } from './components/pacientes/pacientes';
import { Citas } from './components/citas/citas';
import { Notificaciones } from './components/notificaciones/notificaciones';

export const routes: Routes = [
  {
    path: 'estudios',
    component: Estudios,
    title: 'Estudios',
  },
  {
    path: 'informes',
    component: Informes,
    title: 'Informes',
  },
  {
    path: 'pacientes',
    component: Pacientes,
    title: 'Pacientes',
  },
  {
    path: 'citas',
    component: Citas,
    title: 'Citas',
  },
  {
    path: 'notificaciones',
    component: Notificaciones,
    title: 'Notificaciones',
  },
  {
    path: 'login',
    loadComponent: () => import('./components/login/login').then((m) => m.LoginComponent),
  },
  {
    path: '',
    redirectTo: '/estudios',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: '/estudios',
  },
];
