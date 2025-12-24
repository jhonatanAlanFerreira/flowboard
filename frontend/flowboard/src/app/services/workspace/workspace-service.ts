import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { Workspace } from '../../models';

@Injectable({ providedIn: 'root' })
export class WorkspaceService {
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
}
