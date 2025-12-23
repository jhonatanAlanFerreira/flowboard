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
  @Output() onDelete = new EventEmitter();
  @Input({ required: true }) task!: Task;

  deletingList = input(false);

  changeTaskIsDone() {
    // this.service.changeTaskIsDone(this.task.id, this.task.done).subscribe();
  }
}
