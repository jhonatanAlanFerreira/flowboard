import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigService } from '../../config.service';
import { Task } from '../../models';

@Injectable({ providedIn: 'root' })
export class TaskService {
  constructor(
    private http: HttpClient,
    private config: ConfigService,
  ) {}

  create(data: { description: string; tasklistId: number }) {
    return this.http.post(`${this.config.apiBaseUrl}/api/me/task`, data);
  }

  delete(taskId: number) {
    return this.http.delete(`${this.config.apiBaseUrl}/api/me/task/${taskId}`);
  }

  update(task: Task) {
    return this.http.put(`${this.config.apiBaseUrl}/api/me/task/${task.id}`, {
      ...task,
    });
  }

  reorder(newTasklistId: number, sourceTasklistId: number, order: number[]) {
    return this.http.put(`${this.config.apiBaseUrl}/api/me/tasks/reorder`, {
      newTasklistId,
      sourceTasklistId,
      order,
    });
  }
}
