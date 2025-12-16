import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  constructor(private http: HttpClient, private config: ConfigService) {}

  login(data: { email: string; password: string }) {
    return this.http.post(`${this.config.apiBaseUrl}/login`, data);
  }
}
