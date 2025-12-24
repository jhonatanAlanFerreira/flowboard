import { Component, EventEmitter, Output, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Task, Tasklist } from '../../../../models';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
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
import { TasklistService } from '../../../../services/tasklist/tasklist-service';

@Component({
  selector: 'app-tasklist-component',
  imports: [
    TaskComponent,
    ReactiveFormsModule,
    FormsModule,
    Button,
    EditButtonComponent,
    CdkDrag,
    CdkScrollable,
    CdkDropList,
    Divider,
  ],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent {
  @Output() onTaskCreate = new EventEmitter();
  @Output() onTaskDelete = new EventEmitter<{ taskId: number }>();
  @Output() onTasklistDelete = new EventEmitter<{ tasklistId: number }>();

  tasklist = input<Tasklist>();
  isDeleting = input(false);
  taskIdDeleting = input<number>();

  constructor(private tasklistService: TasklistService) {}

  onDropTask(event: CdkDragDrop<Task[] | undefined>) {
    if (!event.container.data || !event.previousContainer.data) {
      return;
    }

    if (event.previousContainer === event.container) {
      moveItemInArray(
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
    }

    this.tasklistService
      .reorderTasks(
        this.tasklist()!.id,
        event.item.data.tasklist_id,
        event.container.data.map((t) => t.id),
      )
      .subscribe();
  }

  deleteTasklist() {
    this.onTasklistDelete.emit({ tasklistId: this.tasklist()!.id });
  }

  isTaskDeleting(task: Task) {
    return this.isDeleting() || task.id == this.taskIdDeleting();
  }

  deleteTask({ taskId }: { taskId: number }) {
    this.onTaskDelete.emit({ taskId });
  }
}
