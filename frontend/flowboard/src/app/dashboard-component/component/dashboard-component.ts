import { Component, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Workspace } from '../dashboard-interfaces';
import { DashboardService } from '../services/dashboard-service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard-component',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  workspaceControl = new FormControl(null);
  workspaces = signal<Workspace[]>([]);
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
}
