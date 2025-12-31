import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { Workspace } from '../../models';

@Injectable({ providedIn: 'root' })
export class WorkspaceService {
  private pollingInterval?: any;

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

  startPolling(onDone: (workspace: any) => void, onFailed: () => void) {
    if (this.pollingInterval) return;

    this.pollingInterval = setInterval(() => {
      this.getLatestStatus().subscribe((res) => {
        if (res.status === 'done') {
          this.stopPolling();
          localStorage.removeItem('aiWorkspacePending');
          onDone(res.workspace);
        }

        if (res.status === 'empty') {
          this.stopPolling();
          localStorage.removeItem('aiWorkspacePending');
        }

        if (res.status === 'failed') {
          this.stopPolling();
          localStorage.removeItem('aiWorkspacePending');
          onFailed();
        }
      });
    }, 5000);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }

  get isGenerating(): boolean {
    return localStorage.getItem('aiWorkspacePending') === 'true';
  }
}
