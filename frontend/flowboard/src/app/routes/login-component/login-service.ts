import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  login(data: { email: string; password: string }) {
    return this.http
      .post<{
        access_token: string;
      }>(`${this.config.apiBaseUrl}/api/login`, data)
      .pipe(
        tap((res) => {
          localStorage.setItem('token', res.access_token);
        }),
      );
  }
}
