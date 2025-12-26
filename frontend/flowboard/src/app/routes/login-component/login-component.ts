import { Component } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { LoginService } from '../../services/login/login-service';
import { Router } from '@angular/router';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule, FormsModule, ToastModule],
  providers: [MessageService],
  templateUrl: './login-component.html',
  styleUrl: './login-component.css',
})
export class LoginComponent {
  loginFormGroup: FormGroup;

  constructor(
    private fb: FormBuilder,
    private service: LoginService,
    private router: Router,
    private messageService: MessageService,
  ) {
    this.loginFormGroup = this.fb.group({
      email: '',
      password: '',
    });
  }

  login() {
    this.service.login(this.loginFormGroup.value).subscribe({
      next: () => this.router.navigate(['']),
      error: (err) => {
        let detail = 'Something went wrong. Please try again.';

        if (err.status === 0) {
          detail =
            'Cannot connect to the server. Check your internet connection.';
        } else if (err.status === 401 || err.status === 422) {
          detail = 'Incorrect username or password.';
        } else if (err.status >= 500) {
          detail = 'Server error. Please try again later.';
        }

        this.messageService.add({
          severity: 'error',
          summary: 'Login Failed',
          detail,
        });
      },
    });
  }
}
