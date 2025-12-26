import { Component } from '@angular/core';
import {
  Validators,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
} from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { LoginService } from '../../services/login/login-service';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-register-component',
  imports: [ReactiveFormsModule, RouterModule],
  templateUrl: './register-component.html',
  styleUrl: './register-component.css',
})
export class RegisterComponent {
  registerForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private service: LoginService,
    private router: Router,
    private messageService: MessageService,
  ) {
    this.registerForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  register() {
    if (this.registerForm.invalid) return;

    this.service.register(this.registerForm.value).subscribe({
      next: (res) => {
        localStorage.setItem('token', res.access_token);

        this.router.navigate(['/']);
      },
      error: (err) => {
        let detail = 'Registration failed. Please try again.';

        if (err.status === 0) {
          detail =
            'Cannot connect to the server. Check your internet connection.';
        } else if (err.status === 422) {
          detail = err.error.message;
          console.log(err)
        }

        this.messageService.add({
          severity: 'error',
          summary: 'Register Failed',
          detail,
        });
      },
    });
  }
}
