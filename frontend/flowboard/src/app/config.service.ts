import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private config!: { apiBaseUrl: string };

  constructor(private http: HttpClient) {}

  load(): Promise<void> {
    return firstValueFrom(
      this.http.get<{ apiBaseUrl: string }>('/config/config.json'),
    ).then((config) => {
      let apiBaseUrl = config.apiBaseUrl;

      if (apiBaseUrl.startsWith(':')) {
        apiBaseUrl = `${window.location.protocol}//${window.location.hostname}${apiBaseUrl}`;
      }

      this.config = { apiBaseUrl };
    });
  }

  get apiBaseUrl(): string {
    return this.config.apiBaseUrl;
  }
}
