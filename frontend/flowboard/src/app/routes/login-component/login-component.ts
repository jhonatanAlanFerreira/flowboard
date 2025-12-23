import { Component } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { LoginService } from '../../services/login/login-service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './login-component.html',
  styleUrl: './login-component.css',
})
export class LoginComponent {
  loginFormGroup: FormGroup;

  constructor(
    private fb: FormBuilder,
    private service: LoginService,
    private router: Router,
  ) {
    this.loginFormGroup = this.fb.group({
      email: '',
      password: '',
    });
  }

  login() {
    this.service
      .login(this.loginFormGroup.value)
      .subscribe(() => this.router.navigate(['']));
  }
}
