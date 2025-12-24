import { Component, EventEmitter, Input, Output, input } from '@angular/core';
import { Task } from '../../../../models';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent, FormsModule],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent {
  @Output() onDelete = new EventEmitter<{ taskId: number }>();
  @Input({ required: true }) task!: Task;

  isDeleting = input(false);

  update() {
    // this.service.changeTaskIsDone(this.task.id, this.task.done).subscribe();
  }

  deleteTask() {
    this.onDelete.emit({ taskId: this.task.id });
  }
}
