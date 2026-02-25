import { Component, EventEmitter, Input, Output, input } from '@angular/core';
import { Task } from '../../../../models';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../../../services/task/task-service';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent, FormsModule],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent {
  @Output() onDelete = new EventEmitter<{ taskId: number }>();
  @Output() onEdit = new EventEmitter<Task>();
  @Input({ required: true }) task!: Task;

  isDeleting = input(false);
  isEditing = input(false);

  editButtonItems: MenuItem[] = [
    {
      label: 'Edit',
      icon: 'pi pi-pencil',
      command: () => this.editTask(),
    },
    {
      label: 'Delete',
      icon: 'pi pi-trash',
      iconClass: 'text-red-500',
      labelClass: 'text-red-500',
      command: () => this.deleteTask(),
    },
  ];

  constructor(private taskService: TaskService) {}

  update() {
    this.taskService.update(this.task).subscribe();
  }

  deleteTask() {
    this.onDelete.emit({ taskId: this.task.id });
  }

  editTask() {
    this.onEdit.emit(this.task);
  }

  get hasMatchesSearchBackground() {
    return this.task.matchesSearch && !this.isDeleting() && !this.isEditing();
  }
}
