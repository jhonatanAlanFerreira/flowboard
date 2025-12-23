import { Component, EventEmitter, Input, Output, input } from '@angular/core';
import { Task } from '../../../../models';
import { DashboardService } from '../../dashboard-service';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import { FormsModule } from '@angular/forms';
import { Dialog } from 'primeng/dialog';
import { Button } from 'primeng/button';

@Component({
  selector: 'app-task-component',
  imports: [EditButtonComponent, FormsModule, Dialog, Button],
  templateUrl: './task-component.html',
  styleUrl: './task-component.css',
})
export class TaskComponent {
  @Output() onDelete = new EventEmitter();
  @Input({ required: true }) task!: Task;
  deletingList = input(false);
  isDeletingModalOpen = false;

  constructor(private service: DashboardService) {}

  delete() {
    this.service.deleteTask(this.task.id).subscribe(() => this.onDelete.emit());
  }

  changeTaskIsDone() {
    this.service.changeTaskIsDone(this.task.id, this.task.done).subscribe();
  }

  onDeleting() {
    this.isDeletingModalOpen = true;
  }
}
