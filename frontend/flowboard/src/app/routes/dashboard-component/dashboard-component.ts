import { Component, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Tasklist, Workspace } from '../../models';
import { TasklistComponent } from './components/tasklist-component/tasklist-component';
import { DropdownComponent } from '../../components/dropdown-component/dropdown-component';
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { EditButtonComponent } from '../../components/edit-button-component/edit-button-component';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  CdkDropListGroup,
  moveItemInArray,
} from '@angular/cdk/drag-drop';
import { WorkspaceService } from '../../services/workspace/workspace-service';
import { TasklistService } from '../../services/tasklist/tasklist-service';
import { DialogComponent } from '../../components/dialog-component/dialog-component';
import { TaskService } from '../../services/task/task-service';
import { WorkspaceModalComponent } from './modals/workspace-modal-component/workspace-modal-component';

@Component({
  selector: 'app-dashboard-component',
  imports: [
    ReactiveFormsModule,
    CommonModule,
    TasklistComponent,
    DropdownComponent,
    DialogModule,
    ButtonModule,
    EditButtonComponent,
    CdkDropListGroup,
    CdkDropList,
    CdkDrag,
    DialogComponent,
    WorkspaceModalComponent,
  ],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  workspaceControl = new FormControl<Workspace | null>(null);

  isWorkspaceModalOpen: {
    opened: boolean;
    data: Workspace | null;
  } = {
    opened: false,
    data: null,
  };
  isWorkspaceDeletingModalOpen = false;

  isListModalOpen = false;
  isListDeletingModalOpen: {
    opened: boolean;
    data: { tasklistId: number } | null;
  } = {
    opened: false,
    data: null,
  };

  isTaskModalOpen = false;
  isTaskDeletingModalOpen: {
    opened: boolean;
    data: { taskId: number } | null;
  } = {
    opened: false,
    data: null,
  };

  workspaces = signal<Workspace[]>([]);
  tasklists = signal<Tasklist[]>([]);
  loading = signal(true);

  constructor(
    private workspaceService: WorkspaceService,
    private tasklistService: TasklistService,
    private taskService: TaskService,
  ) {
    this.workspaceControl.valueChanges.subscribe(() => {
      this.listTasklistsFromWorkspace();
    });
  }

  ngOnInit(): void {
    this.listWorkspaces();
  }

  onDropTasklist(event: CdkDragDrop<Tasklist>) {
    moveItemInArray(this.tasklists(), event.previousIndex, event.currentIndex);

    if (this.workspaceControl.value) {
      this.workspaceService
        .reorderTasklists(
          this.workspaceControl.value.id,
          this.tasklists().map((t) => t.id),
        )
        .subscribe();
    }
  }

  listWorkspaces() {
    this.loading.set(true);

    this.workspaceService.list().subscribe((res) => {
      this.workspaces.set(res);
      this.loading.set(false);
    });
  }

  listTasklistsFromWorkspace() {
    const { value } = this.workspaceControl;

    if (value) {
      this.loading.set(true);

      this.tasklistService.listFromWorkspace(value.id).subscribe((res) => {
        this.tasklists.set(res);
        this.loading.set(false);
      });
    }
  }

  deleteWorkspace() {
    this.isWorkspaceDeletingModalOpen = false;
    this.loading.set(true);

    this.workspaceService
      .delete(this.workspaceControl.value!.id)
      .subscribe(() => {
        this.workspaceControl.reset();
        this.listWorkspaces();
        this.tasklists.set([]);
      });
  }

  onTasklistDelete({ tasklistId }: { tasklistId: number }) {
    setTimeout(() => {
      this.isListDeletingModalOpen = {
        opened: true,
        data: { tasklistId },
      };
    });
  }

  onWorkspaceDelete() {
    setTimeout(() => {
      this.isWorkspaceDeletingModalOpen = true;
    });
  }

  deleteTasklist() {
    this.loading.set(true);

    this.tasklistService
      .delete(this.isListDeletingModalOpen.data!.tasklistId)
      .subscribe(() => {
        this.listTasklistsFromWorkspace();
      });

    this.isListDeletingModalOpen = {
      opened: false,
      data: null,
    };
  }

  isListDeleting(tasklist: Tasklist) {
    const { data, opened } = this.isListDeletingModalOpen;

    const isWorkspaceDeleting = this.isWorkspaceDeletingModalOpen;
    const isTasklistDeleting = opened && data?.tasklistId == tasklist.id;

    return isWorkspaceDeleting || isTasklistDeleting;
  }

  onTaskDelete({ taskId }: { taskId: number }) {
    setTimeout(() => {
      this.isTaskDeletingModalOpen = {
        opened: true,
        data: { taskId },
      };
    });
  }

  onCancelTaskDeleting() {
    this.isTaskDeletingModalOpen = {
      data: null,
      opened: false,
    };
  }

  deleteTask() {
    this.loading.set(true);

    this.taskService
      .delete(this.isTaskDeletingModalOpen.data!.taskId)
      .subscribe(() => {
        this.listTasklistsFromWorkspace();
      });

    this.isTaskDeletingModalOpen = {
      opened: false,
      data: null,
    };
  }

  onAddWorkspace() {
    this.isWorkspaceModalOpen = {
      opened: true,
      data: null,
    };
  }

  onWorkspaceEdit() {
    setTimeout(() => {
      this.isWorkspaceModalOpen = {
        opened: true,
        data: this.workspaceControl.value,
      };
    });
  }

  onWorkspaceModalCancel() {
    this.isWorkspaceModalOpen = {
      opened: false,
      data: null,
    };
  }

  onWorkspaceModalSave(workspace: Workspace) {
    this.isWorkspaceModalOpen = {
      opened: false,
      data: null,
    };

    this.workspaceControl.setValue(workspace);

    this.listWorkspaces();
  }
}
