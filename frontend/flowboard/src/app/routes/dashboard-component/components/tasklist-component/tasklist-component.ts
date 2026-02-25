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
import { MenuItem } from 'primeng/api';

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
  @Output() onTasklistDelete = new EventEmitter<{ tasklistId: number }>();
  @Output() onTasklistEdit = new EventEmitter<Tasklist>();
  @Output() onTaskCreate = new EventEmitter<{ tasklistId: number }>();
  @Output() onTaskDelete = new EventEmitter<{ taskId: number }>();
  @Output() onTaskEdit = new EventEmitter<Task>();
  @Output() onTaskDropped = new EventEmitter();
  @Output() onTaskDoneReorder = new EventEmitter();
  @Output() onSendListToWorkspace = new EventEmitter<Tasklist>();

  tasklist = input<Tasklist>();
  isDeleting = input(false);
  taskIdDeleting = input<number>();
  taskIdEditing = input<number>();

  editButtonItems: MenuItem[] = [
    {
      label: 'Move done tasks to top',
      labelClass: 'text-nowrap',
      icon: 'pi pi-sort-amount-up',
      command: () => this.moveDoneTasks('top'),
    },
    {
      label: 'Move done tasks to bottom',
      labelClass: 'text-nowrap',
      icon: 'pi pi-sort-amount-down',
      command: () => this.moveDoneTasks('bottom'),
    },
    {
      label: 'Copy this list to another workspace',
      labelClass: 'text-nowrap',
      icon: 'pi pi-clone',
      command: () => this.onSendListToWorkspace.emit(this.tasklist()),
    },
    {
      label: 'Add new Task',
      icon: 'pi pi-plus',
      command: () => this.createTask(),
    },
    {
      label: 'Edit',
      icon: 'pi pi-pencil',
      command: () => this.editTasklist(),
    },
    {
      label: 'Delete',
      icon: 'pi pi-trash',
      iconClass: 'text-red-500',
      labelClass: 'text-red-500',
      command: () => this.deleteTasklist(),
    },
  ];

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

    this.applyTaskOrder(
      event.container.data,
      event.item.data.tasklist_id,
    ).subscribe();
  }

  deleteTasklist() {
    this.onTasklistDelete.emit({ tasklistId: this.tasklist()!.id });
  }

  isTaskDeleting(task: Task) {
    return this.isDeleting() || task.id == this.taskIdDeleting();
  }

  isTaskEditing(task: Task) {
    return task.id == this.taskIdEditing();
  }

  deleteTask({ taskId }: { taskId: number }) {
    this.onTaskDelete.emit({ taskId });
  }

  editTasklist() {
    this.onTasklistEdit.emit(this.tasklist());
  }

  createTask() {
    this.onTaskCreate.emit({ tasklistId: this.tasklist()?.id! });
  }

  editTask(task: Task) {
    this.onTaskEdit.emit(task);
  }

  moveDoneTasks(position: 'top' | 'bottom') {
    const { tasks } = this.tasklist()!;

    if (tasks?.length) {
      const done = tasks.filter((t) => t.done);
      const active = tasks.filter((t) => !t.done);

      const newOrder =
        position === 'top' ? [...done, ...active] : [...active, ...done];

      this.applyTaskOrder(newOrder, this.tasklist()!.id).subscribe(() => {
        this.onTaskDoneReorder.emit();
      });
    }
  }

  private applyTaskOrder(tasks: Task[], tasklistId: number) {
    this.onTaskDropped.emit();

    return this.tasklistService.reorderTasks(
      this.tasklist()!.id,
      tasklistId,
      tasks.map((t) => t.id),
    );
  }
}
