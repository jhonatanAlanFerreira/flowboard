import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RegisterComponent } from './register-component';
import { LoginService } from '../../services/login/login-service';
import { MessageService } from 'primeng/api';
import { Router, provideRouter } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('RegisterComponent', () => {
  let component: RegisterComponent;
  let fixture: ComponentFixture<RegisterComponent>;
  let router: Router;

  const loginServiceMock = {
    register: vi.fn(),
  };
  const messageServiceMock = {
    add: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterComponent, ReactiveFormsModule],
      providers: [
        provideRouter([]),
        { provide: LoginService, useValue: loginServiceMock },
        { provide: MessageService, useValue: messageServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;

    router = TestBed.inject(Router);

    fixture.detectChanges();
  });

  it('should navigate to root on successful registration', () => {
    const mockResponse = { access_token: 'mock-token' };
    loginServiceMock.register.mockReturnValue(of(mockResponse));

    const navigateSpy = vi.spyOn(router, 'navigate');
    const storageSpy = vi.spyOn(Storage.prototype, 'setItem');

    component.registerForm.patchValue({
      name: 'Test User',
      email: 'test@example.com',
      password: 'password123',
    });

    component.register();

    expect(storageSpy).toHaveBeenCalledWith('token', 'mock-token');
    expect(navigateSpy).toHaveBeenCalledWith(['/']);
  });
});
