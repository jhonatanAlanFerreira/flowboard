import { Routes } from '@angular/router';
import { DashboardComponent } from './routes/dashboard-component/dashboard-component';
import { LoginComponent } from './routes/login-component/login-component';
import { RegisterComponent } from './routes/register-component/register-component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
];
