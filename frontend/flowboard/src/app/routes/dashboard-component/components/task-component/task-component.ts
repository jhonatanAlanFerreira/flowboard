import {
  Component,
  EventEmitter,
  Input,
  Output,
  input,
  signal,
} from '@angular/core';
import { Task } from '../../../../models';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../../../services/task/task-service';
import { MenuItem } from 'primeng/api';
import { Button } from 'primeng/button';
import { ClipboardModule } from '@angular/cdk/clipboard';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent, FormsModule, Button, ClipboardModule],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent {
  @Output() onDelete = new EventEmitter<{ taskId: number }>();
  @Output() onEdit = new EventEmitter<Task>();
  @Output() onSend = new EventEmitter<Task>();
  @Input({ required: true }) task!: Task;

  isDeleting = input(false);
  isEditing = input(false);

  contentCopied = signal(false);

  editButtonItems: MenuItem[] = [
    {
      label: 'Send this task to another workspace',
      icon: 'pi pi-send',
      command: () => this.sendTask(),
    },
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

  sendTask() {
    this.onSend.emit(this.task);
  }

  showCopied() {
    this.contentCopied.set(true);

    setTimeout(() => {
      this.contentCopied.set(false);
    }, 1500);
  }
  get hasMatchesSearchBackground() {
    return this.task.matchesSearch && !this.isDeleting() && !this.isEditing();
  }
}
