import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { User } from '../../models';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  private user$ = new BehaviorSubject<User | null>(null);

  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  login(data: { email: string; password: string }) {
    return this.http
      .post<{
        access_token: string;
        user: User;
      }>(`${this.config.apiBaseUrl}/api/login`, data)
      .pipe(
        tap((res) => {
          this.setSession(res.access_token, res.user);
        }),
      );
  }

  register(data: { name: string; password: string; email: string }) {
    return this.http
      .post<{
        access_token: string;
        user: User;
      }>(`${this.config.apiBaseUrl}/api/register`, data)
      .pipe(
        tap((res) => {
          this.setSession(res.access_token, res.user);
        }),
      );
  }

  getUser(): Observable<User | null> {
    if (this.user$.value) {
      return this.user$.asObservable();
    }

    if (!this.getToken()) {
      return this.user$.asObservable();
    }

    this.http.get<User>(`${this.config.apiBaseUrl}/api/me`).subscribe({
      next: (user) => this.user$.next(user),
      error: () => this.clearSession(),
    });

    return this.user$.asObservable();
  }

  logout() {
    this.clearSession();
  }

  private setSession(token: string, user: User) {
    localStorage.setItem('token', token);
    this.user$.next(user);
  }

  private clearSession() {
    localStorage.removeItem('token');
    localStorage.removeItem('lastUsedWorkspace');
    this.user$.next(null);
  }

  private getToken(): string | null {
    return localStorage.getItem('token');
  }
}
