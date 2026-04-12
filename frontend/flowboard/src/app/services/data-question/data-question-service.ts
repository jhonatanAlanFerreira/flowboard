import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ConfigService } from '../../config.service';

@Injectable({
  providedIn: 'root',
})
export class DataQuestionService {
  private pollingInterval?: any;

  private doneAskAiSubject = new BehaviorSubject<any | null>(null);
  doneAskAi$ = this.doneAskAiSubject.asObservable();

  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  askAI(data: { prompt: string }): Observable<any> {
    return this.http.post(
      `${this.config.apiBaseUrl}/api/me/ai/data-question`,
      data,
    );
  }

  getLatestStatus(): Observable<any> {
    return this.http.get<any>(
      `${this.config.apiBaseUrl}/api/me/ai/data-question/latest`,
      {
        headers: { 'x-skip-status': 'true' },
      },
    );
  }

  private pendingKey(userId: number): string {
    return `askAiPending:${userId}`;
  }

  setPendingAskAi(userId: number): void {
    localStorage.setItem(this.pendingKey(userId), 'true');
  }

  hasPendingAskAi(userId: number): boolean {
    return localStorage.getItem(this.pendingKey(userId)) === 'true';
  }

  clearPendingAskAi(userId: number): void {
    localStorage.removeItem(this.pendingKey(userId));
  }

  startPolling(onFailed: () => void, userId?: number): void {
    if (this.pollingInterval) return;

    this.pollingInterval = setInterval(() => {
      this.getLatestStatus().subscribe({
        next: (res) => {
          if (res.status === 'done') {
            this.cleanupPolling(userId);
            this.doneAskAiSubject.next({
              answer: res.answer,
              source_tasks: res.source_tasks,
            });
            return;
          }

          if (res.status === 'empty') {
            this.cleanupPolling(userId);
            return;
          }

          if (res.status === 'failed') {
            this.cleanupPolling(userId);
            onFailed();
            return;
          }
        },

        error: (err) => {
          if (err.status === 401) {
            this.stopPolling();
            return;
          }

          this.cleanupPolling(userId);
          onFailed();
        },
      });
    }, 5000);
  }

  clearDoneAskAi(): void {
    this.doneAskAiSubject.next(null);
  }

  stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }

  private cleanupPolling(userId?: number): void {
    this.stopPolling();

    if (userId) {
      this.clearPendingAskAi(userId);
    }
  }
}
