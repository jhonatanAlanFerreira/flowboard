import { Component, EventEmitter, Output, input } from '@angular/core';
import { Task } from '../../../../models';
import { DashboardService } from '../../dashboard-service';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent {
  @Output() onDelete = new EventEmitter();
  task = input<Task>();

  constructor(private service: DashboardService) {}

  delete() {
    this.service.deleteTask(this.task()!.id).subscribe(() => this.onDelete.emit());
  }
}
