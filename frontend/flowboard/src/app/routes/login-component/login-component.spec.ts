import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login-component';
import { LoginService } from '../../services/login/login-service';
import { MessageService } from 'primeng/api';
import { Router, provideRouter } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let router: Router;

  const loginServiceMock = {
    login: vi.fn(),
  };
  const messageServiceMock = {
    add: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginComponent, ReactiveFormsModule],
      providers: [
        provideRouter([]),
        { provide: LoginService, useValue: loginServiceMock },
        { provide: MessageService, useValue: messageServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should navigate to root on successful login', () => {
    loginServiceMock.login.mockReturnValue(of({ access_token: 'abc' }));
    const navigateSpy = vi.spyOn(router, 'navigate');

    component.loginFormGroup.patchValue({
      email: 'test@test.com',
      password: 'password123',
    });

    component.login();

    expect(loginServiceMock.login).toHaveBeenCalledWith({
      email: 'test@test.com',
      password: 'password123',
    });
    expect(navigateSpy).toHaveBeenCalledWith(['']);
  });

  it('should show "Incorrect username or password" on 401 error', () => {
    loginServiceMock.login.mockReturnValue(throwError(() => ({ status: 401 })));

    component.login();

    expect(messageServiceMock.add).toHaveBeenCalledWith({
      severity: 'error',
      summary: 'Login Failed',
      detail: 'Incorrect username or password.',
    });
  });

  it('should show connection error message when status is 0', () => {
    loginServiceMock.login.mockReturnValue(throwError(() => ({ status: 0 })));

    component.login();

    expect(messageServiceMock.add).toHaveBeenCalledWith({
      severity: 'error',
      summary: 'Login Failed',
      detail: 'Cannot connect to the server. Check your internet connection.',
    });
  });

  it('should show server error message when status is 500', () => {
    loginServiceMock.login.mockReturnValue(throwError(() => ({ status: 500 })));

    component.login();

    expect(messageServiceMock.add).toHaveBeenCalledWith({
      severity: 'error',
      summary: 'Login Failed',
      detail: 'Server error. Please try again later.',
    });
  });
});
