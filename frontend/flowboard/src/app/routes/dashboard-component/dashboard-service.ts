import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { Tasklist, Workspace } from '../../models';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  constructor(private http: HttpClient, private config: ConfigService) {}

  listWorkspaces() {
    return this.http.get<Workspace[]>(`${this.config.apiBaseUrl}/api/me/workspaces`);
  }

  listTasklistsFromWorkspace(workspaceId: number) {
    return this.http.get<Tasklist[]>(
      `${this.config.apiBaseUrl}/api/me/workspace/${workspaceId}/tasklists`
    );
  }

  createNewList(data: { name: string; workspaceId: number }) {
    return this.http.post(`${this.config.apiBaseUrl}/api/me/tasklist`, data);
  }

  createNewTask(data: { description: string; tasklistId: number }) {
    return this.http.post(`${this.config.apiBaseUrl}/api/me/task`, data);
  }

  createWorkspace(data: { name: string }) {
    return this.http.post(`${this.config.apiBaseUrl}/api/me/workspace`, data);
  }

  deleteTask(taskId: number) {
    return this.http.delete(`${this.config.apiBaseUrl}/api/me/task/${taskId}`);
  }

  deleteTasklist(tasklistId: number) {
    return this.http.delete(`${this.config.apiBaseUrl}/api/me/tasklist/${tasklistId}`);
  }

  deleteWorkspace(workspaceId: number) {
    return this.http.delete(`${this.config.apiBaseUrl}/api/me/workspace/${workspaceId}`);
  }
}
