import {
  Component,
  EventEmitter,
  Output,
  SimpleChange,
  input,
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Task } from '../../../../models';
import { TaskService } from '../../../../services/task/task-service';

@Component({
  selector: 'app-task-modal-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './task-modal-component.html',
  styleUrl: './task-modal-component.css',
})
export class TaskModalComponent {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter();

  task = input<Task | null>(null);
  tasklistId = input.required<number>();
  visible = input(false);

  descriptionControl = new FormControl<string>('');

  constructor(private taskService: TaskService) {}

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['task']) {
      this.descriptionControl.setValue(this.task()?.description || '');
    }
  }

  save() {
    if (this.task()?.id) {
      this.taskService
        .update({
          ...this.task()!,
          description: this.descriptionControl.value!,
        })
        .subscribe(() => {
          this.onSave.emit();
        });
    } else {
      this.taskService
        .create({
          description: this.descriptionControl.value!,
          tasklistId: this.tasklistId(),
        })
        .subscribe(() => {
          this.onSave.emit();
        });
    }
  }

  onHide() {
    this.descriptionControl.reset();
    this.onCancel.emit();
  }

  get header() {
    return this.task()?.id ? 'Update Task description' : 'Create new Task';
  }
}
