import { Component, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Task, Tasklist, Workspace } from '../../models';
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
import { TasklistModalComponent } from './modals/tasklist-modal-component/tasklist-modal-component';
import { TaskModalComponent } from './modals/task-modal-component/task-modal-component';
import { tap } from 'rxjs';
import { LoadingComponent } from '../../components/loading-component/loading-component';

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
    TasklistModalComponent,
    TaskModalComponent,
    LoadingComponent,
  ],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  workspaceControl = new FormControl<Workspace | null>(null);
  searchControl = new FormControl<string | null>(null);

  isWorkspaceDeletingModalOpen = false;

  isWorkspaceModalOpen: {
    opened: boolean;
    data: Workspace | null;
  } = {
    opened: false,
    data: null,
  };

  isListModalOpen: {
    opened: boolean;
    data: Tasklist | null;
  } = {
    opened: false,
    data: null,
  };

  isListDeletingModalOpen: {
    opened: boolean;
    data: { tasklistId: number } | null;
  } = {
    opened: false,
    data: null,
  };

  isTaskModalOpen: {
    opened: boolean;
    data: { task: Task | null; tasklistId: number } | null;
  } = {
    opened: false,
    data: null,
  };

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
      this.setLastUsedWorkspace();
    });

    this.searchControl.valueChanges.subscribe(() => {
      this.applySearch();
    });
  }

  ngOnInit(): void {
    this.listWorkspaces().subscribe(() => {
      this.getLastUsedWorkspace();
    });
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

  setLastUsedWorkspace() {
    localStorage.setItem(
      'lastUsedWorkspace',
      JSON.stringify(this.workspaceControl.value),
    );
  }

  getLastUsedWorkspace() {
    const lastUsedWorkspaceString = localStorage.getItem('lastUsedWorkspace');
    if (lastUsedWorkspaceString) {
      this.workspaceControl.setValue(JSON.parse(lastUsedWorkspaceString));
    }
  }

  applySearch() {
    const value = this.searchControl.value?.trim().toLowerCase();

    if (!value) {
      this.tasklists().forEach((tk) => {
        tk.hasMatchingTasks = false;
        tk.tasks?.forEach((t) => (t.matchesSearch = false));
      });
      return;
    }

    this.tasklists().forEach((tk) => {
      let hasMatchingTasks = false;

      tk.tasks?.forEach((t) => {
        const matches = t.description.toLowerCase().includes(value);
        t.matchesSearch = matches;
        if (matches) {
          hasMatchingTasks = true;
        }
      });

      tk.hasMatchingTasks = hasMatchingTasks;
    });
  }

  listWorkspaces() {
    return this.workspaceService.list().pipe(
      tap((res) => {
        this.workspaces.set(res);
      }),
    );
  }

  listTasklistsFromWorkspace() {
    const { value } = this.workspaceControl;

    if (value) {
      this.loading.set(true);

      this.tasklistService.listFromWorkspace(value.id).subscribe((res) => {
        this.tasklists.set(res);
        this.loading.set(false);
        this.applySearch();
      });
    }
  }

  deleteWorkspace() {
    this.isWorkspaceDeletingModalOpen = false;

    this.workspaceService
      .delete(this.workspaceControl.value!.id)
      .subscribe(() => {
        this.workspaceControl.reset();
        this.listWorkspaces().subscribe();
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

    this.listWorkspaces().subscribe();
  }

  onCreateNewList() {
    this.isListModalOpen = {
      opened: true,
      data: null,
    };
  }

  onListModalCancel() {
    this.isListModalOpen = {
      opened: false,
      data: null,
    };
  }

  onTasklistEdit(tasklist: Tasklist) {
    setTimeout(() => {
      this.isListModalOpen = {
        opened: true,
        data: tasklist,
      };
    });
  }

  onListModalSave() {
    this.isListModalOpen = {
      opened: false,
      data: null,
    };

    this.listTasklistsFromWorkspace();
  }

  onTaskCreate({ tasklistId }: { tasklistId: number }) {
    this.isTaskModalOpen = {
      opened: true,
      data: {
        task: null,
        tasklistId,
      },
    };
  }

  onTaskModalCancel() {
    this.isTaskModalOpen = {
      opened: false,
      data: null,
    };
  }

  onTaskModalSave() {
    this.isTaskModalOpen = {
      opened: false,
      data: null,
    };

    this.listTasklistsFromWorkspace();
  }

  onTaskEdit(task: Task) {
    setTimeout(() => {
      this.isTaskModalOpen = {
        opened: true,
        data: { task, tasklistId: task.tasklist_id },
      };
    });
  }
}
