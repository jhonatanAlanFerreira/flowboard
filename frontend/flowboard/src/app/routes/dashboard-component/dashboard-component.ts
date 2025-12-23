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
  ],
  templateUrl: './dashboard-component.html',
  styleUrl: './dashboard-component.css',
})
export class DashboardComponent implements OnInit {
  workspaceControl = new FormControl<Workspace | null>(null);

  isWorkspaceModalOpen = false;
  isWorkspaceDeletingModalOpen = false;

  isListModalOpen = false;
  isListDeletingModalOpen = false;

  isTaskModalOpen = false;
  isTaskDeletingModalOpen = false;

  workspaces = signal<Workspace[]>([]);
  tasklists = signal<Tasklist[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.listWorkspaces();
  }

  listWorkspaces() {
    // this.loading.set(true);
    // this.service.listWorkspaces().subscribe((res) => {
    //   this.workspaces.set(res);
    //   this.loading.set(false);
    // });
  }

  listTasklistsFromWorkspace() {
    // this.loading.set(true);
    // this.service
    //   .listTasklistsFromWorkspace(this.workspaceControl.value!.id)
    //   .subscribe((res) => {
    //     this.tasklists.set(res);
    //     this.loading.set(false);
    //   });
  }

  onDropTasklist(event: CdkDragDrop<Tasklist>) {
    moveItemInArray(this.tasklists(), event.previousIndex, event.currentIndex);

    if (this.workspaceControl.value) {
      // this.service
      //   .reorderTasklist(
      //     this.workspaceControl.value.id,
      //     this.tasklists().map((t) => t.id),
      //   )
      //   .subscribe();
    }
  }
}
