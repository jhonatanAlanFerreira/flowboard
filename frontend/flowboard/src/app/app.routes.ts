import { Routes } from '@angular/router';
import { DashboardComponent } from './routes/dashboard-component/dashboard-component';
import { LoginComponent } from './routes/login-component/login-component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'login', component: LoginComponent },
];
