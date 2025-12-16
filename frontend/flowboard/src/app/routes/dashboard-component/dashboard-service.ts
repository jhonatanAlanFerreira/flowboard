import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Workspace } from './dashboard-interfaces';
import { ConfigService } from '../../config.service';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  constructor(private http: HttpClient, private config: ConfigService) {}

  listWorkspaces() {
    return this.http.get<Workspace[]>(`${this.config.apiBaseUrl}/api/me/workspaces`);
  }
}
