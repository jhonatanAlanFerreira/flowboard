import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { ConfigService } from '../../config.service';
import { Workspace } from '../../models';

@Injectable({ providedIn: 'root' })
export class WorkspaceService {
  private pollingInterval?: any;

  private doneWorkspaceSubject = new BehaviorSubject<Workspace | null>(null);
  doneWorkspace$ = this.doneWorkspaceSubject.asObservable();

  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  list() {
    return this.http.get<Workspace[]>(
      `${this.config.apiBaseUrl}/api/me/workspaces`,
    );
  }

  create(data: { name: string }) {
    return this.http.post<Workspace>(
      `${this.config.apiBaseUrl}/api/me/workspace`,
      data,
    );
  }

  createByAI(data: { prompt: string }) {
    return this.http.post(
      `${this.config.apiBaseUrl}/api/me/ai/workspaces`,
      data,
    );
  }

  update(data: { name: string; id: number }) {
    return this.http.put<Workspace>(
      `${this.config.apiBaseUrl}/api/me/workspace/${data.id}`,
      data,
    );
  }

  delete(workspaceId: number) {
    return this.http.delete(
      `${this.config.apiBaseUrl}/api/me/workspace/${workspaceId}`,
    );
  }

  reorderTasklists(workspaceId: number, order: number[]) {
    return this.http.put(`${this.config.apiBaseUrl}/api/me/tasklists/reorder`, {
      workspaceId,
      order,
    });
  }

  getLatestStatus() {
    return this.http.get<{
      status: 'empty' | 'pending' | 'processing' | 'done' | 'failed';
      workspace: null | Workspace;
    }>(`${this.config.apiBaseUrl}/api/me/ai/workspaces/latest`, {
      headers: { 'x-skip-status': 'true' },
    });
  }

  private pendingKey(userId: number) {
    return `aiWorkspacePending:${userId}`;
  }

  setPendingWorkspace(userId: number) {
    localStorage.setItem(this.pendingKey(userId), 'true');
  }

  hasPendingWorkspace(userId: number): boolean {
    return localStorage.getItem(this.pendingKey(userId)) === 'true';
  }

  clearPendingWorkspace(userId: number) {
    localStorage.removeItem(this.pendingKey(userId));
  }

  startPolling(onFailed: () => void, userId?: number) {
    if (this.pollingInterval) return;

    this.pollingInterval = setInterval(() => {
      this.getLatestStatus().subscribe({
        next: (res) => {
          if (res.status === 'done') {
            this.cleanupPolling(userId);
            this.doneWorkspaceSubject.next(res.workspace!);
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

  clearDoneWorkspace() {
    this.doneWorkspaceSubject.next(null);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }

  private cleanupPolling(userId?: number) {
    this.stopPolling();

    if (userId) {
      this.clearPendingWorkspace(userId);
    }
  }
}
