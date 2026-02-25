import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { Tasklist } from '../../models';

@Injectable({ providedIn: 'root' })
export class TasklistService {
  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  listFromWorkspace(workspaceId: number) {
    return this.http.get<Tasklist[]>(
      `${this.config.apiBaseUrl}/api/me/workspace/${workspaceId}/tasklists`,
    );
  }

  create(data: { name: string; workspaceId: number }) {
    return this.http.post<Tasklist>(
      `${this.config.apiBaseUrl}/api/me/tasklist`,
      data,
    );
  }

  update(data: { name: string; id: number }) {
    return this.http.put<Tasklist>(
      `${this.config.apiBaseUrl}/api/me/tasklist/${data.id}`,
      data,
    );
  }

  copyList(tasklistId: number, workspaceId: number) {
    return this.http.put<Tasklist>(
      `${this.config.apiBaseUrl}/api/me/copy-list/${tasklistId}/workspace/${workspaceId}`,
      {},
    );
  }

  delete(tasklistId: number) {
    return this.http.delete(
      `${this.config.apiBaseUrl}/api/me/tasklist/${tasklistId}`,
    );
  }

  reorderTasks(
    newTasklistId: number,
    sourceTasklistId: number,
    order: number[],
  ) {
    return this.http.put(`${this.config.apiBaseUrl}/api/me/tasks/reorder`, {
      newTasklistId,
      sourceTasklistId,
      order,
    });
  }
}
