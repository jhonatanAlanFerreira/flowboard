import { Component, EventEmitter, OnChanges, Output, SimpleChange, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Task, Tasklist } from '../../../../models';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DashboardService } from '../../dashboard-service';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { Divider } from 'primeng/divider';

@Component({
  selector: 'app-tasklist-component',
  imports: [
    TaskComponent,
    ReactiveFormsModule,
    FormsModule,
    Button,
    Dialog,
    EditButtonComponent,
    CdkDrag,
    CdkScrollable,
    CdkDropList,
    Divider,
  ],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent implements OnChanges {
  @Output() onTaskCreated = new EventEmitter();
  @Output() onTaskDelete = new EventEmitter();
  @Output() onTasklistDelete = new EventEmitter();

  tasklist = input<Tasklist>();
  workspaceDeleting = input(false);

  newTaskFormGroup: FormGroup;
  isTaskModalOpen = false;
  isDeletingModalOpen = false;

  constructor(private fb: FormBuilder, private service: DashboardService) {
    this.newTaskFormGroup = this.fb.group({
      description: '',
      tasklistId: null,
    });
  }

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['tasklist']) {
      this.newTaskFormGroup.get('tasklistId')?.setValue(changes['tasklist'].currentValue.id);
    }
  }

  createNewTask() {
    this.isTaskModalOpen = false;

    this.service.createNewTask(this.newTaskFormGroup.value).subscribe(() => {
      this.onTaskCreated.emit();
      this.newTaskFormGroup.reset();
    });
  }

  delete() {
    this.service.deleteTasklist(this.tasklist()!.id).subscribe(() => this.onTasklistDelete.emit());
  }

  onDropTask(event: CdkDragDrop<Task[] | undefined>) {
    if (!event.container.data || !event.previousContainer.data) {
      return;
    }

    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    }

    this.service
      .reorderTasks(
        this.tasklist()!.id,
        event.item.data.tasklist_id,
        event.container.data.map((t) => t.id)
      )
      .subscribe();
  }
}
