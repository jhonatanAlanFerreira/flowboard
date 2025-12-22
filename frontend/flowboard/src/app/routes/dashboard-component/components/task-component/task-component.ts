import { Component, EventEmitter, OnChanges, Output, SimpleChange, input } from '@angular/core';
import { Task } from '../../../../models';
import { DashboardService } from '../../dashboard-service';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent, FormsModule],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent implements OnChanges {
  @Output() onDelete = new EventEmitter();
  task = input<Task>();
  done = false;

  constructor(private service: DashboardService) {}

  ngOnChanges(changes: { [propName: string]: SimpleChange<Task> }): void {
    this.done = changes['task'].currentValue.done;
  }

  delete() {
    this.service.deleteTask(this.task()!.id).subscribe(() => this.onDelete.emit());
  }

  changeTaskIsDone() {
    this.service.changeTaskIsDone(this.task()!.id, this.done).subscribe(() => {});
  }
}
