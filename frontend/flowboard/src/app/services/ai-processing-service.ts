import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../config.service';

@Injectable({
  providedIn: 'root',
})
export class AiProcessingService {
  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  askAI(data: { prompt: string }) {
    return this.http.post(
      `${this.config.apiBaseUrl}/api/me/ai/data-question`,
      data,
    );
  }
}
