import { Component, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { DashboardService } from './dashboard-service';
import { CommonModule } from '@angular/common';
import { Tasklist, Workspace } from '../../models';
import { TasklistComponent } from './components/tasklist-component/tasklist-component';

@Component({
  selector: 'app-dashboard-component',
  imports: [ReactiveFormsModule, CommonModule, TasklistComponent],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  workspaceControl = new FormControl(null);
  workspaces = signal<Workspace[]>([]);
  tasklists = signal<Tasklist[]>([]);
  loading = signal(true);

  constructor(private service: DashboardService) {}

  ngOnInit(): void {
    this.listWorkspaces();
  }

  listWorkspaces() {
    this.service.listWorkspaces().subscribe((res) => {
      this.workspaces.set(res);
      this.loading.set(false);
    });
  }

  listTasklistsFromWorkspace() {
    const { value } = this.workspaceControl;

    if (value) {
      this.loading.set(true);

      this.service.listTasklistsFromWorkspace(value).subscribe((res) => {
        this.tasklists.set(res);
        this.loading.set(false);
      });
    }
  }
}
