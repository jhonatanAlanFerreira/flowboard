import { Component, EventEmitter, Output, input } from '@angular/core';
import { Task } from '../../../../models';
import { DashboardService } from '../../dashboard-service';

@Component({
  selector: 'app-task-component',
  imports: [],
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
