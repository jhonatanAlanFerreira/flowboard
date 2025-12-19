import { Component, OnInit, signal } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { DashboardService } from './dashboard-service';
import { CommonModule } from '@angular/common';
import { Tasklist, Workspace } from '../../models';
import { TasklistComponent } from './components/tasklist-component/tasklist-component';
import { DropdownComponent } from '../../components/dropdown-component/dropdown-component';

@Component({
  selector: 'app-dashboard-component',
  imports: [ReactiveFormsModule, CommonModule, TasklistComponent, DropdownComponent],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  newListFormGroup: FormGroup;
  workspaceControl = new FormControl<Workspace | null>(null);
  newWorkspaceControl = new FormControl<string | null>(null);
  workspaces = signal<Workspace[]>([]);
  tasklists = signal<Tasklist[]>([]);
  loading = signal(true);

  constructor(private fb: FormBuilder, private service: DashboardService) {
    this.newListFormGroup = this.fb.group({
      name: '',
      workspaceId: null,
    });

    this.workspaceControl.valueChanges.subscribe((value) =>
      this.newListFormGroup.get('workspaceId')?.setValue(value?.id)
    );

    this.workspaceControl.valueChanges.subscribe(() => {
      this.listTasklistsFromWorkspace();
    });
  }

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
    this.loading.set(true);

    this.service.listTasklistsFromWorkspace(this.workspaceControl.value!.id).subscribe((res) => {
      this.tasklists.set(res);
      this.loading.set(false);
    });
  }

  createNewList() {
    this.loading.set(true);

    this.service.createNewList(this.newListFormGroup.value).subscribe(() => {
      this.newListFormGroup.get('name')?.reset();
      this.listTasklistsFromWorkspace();
    });
  }

  deleteWorkspace() {
    if (this.workspaceControl.value) {
      this.service.deleteWorkspace(this.workspaceControl.value!.id).subscribe(() => {
        this.workspaceControl.reset();
        this.listWorkspaces();
        this.tasklists.set([]);
      });
    }
  }

  createWorkspace() {
    if (this.newWorkspaceControl.value) {
      this.service
        .createWorkspace({ name: this.newWorkspaceControl.value })
        .subscribe((res: Workspace) => {
          this.newWorkspaceControl.reset();
          this.workspaceControl.setValue(res);
          this.listWorkspaces();
        });
    }
  }

  onAddWorkspace() {
    alert('WIP');
  }
}
