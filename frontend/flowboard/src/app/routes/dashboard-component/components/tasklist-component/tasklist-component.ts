import { Component, EventEmitter, OnChanges, Output, SimpleChange, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Tasklist } from '../../../../models';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DashboardService } from '../../dashboard-service';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';

@Component({
  selector: 'app-tasklist-component',
  imports: [TaskComponent, ReactiveFormsModule, FormsModule, Button, Dialog],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent implements OnChanges {
  @Output() onTaskCreated = new EventEmitter();
  @Output() onTaskDelete = new EventEmitter();
  @Output() onTasklistDelete = new EventEmitter();

  newTaskFormGroup: FormGroup;
  tasklist = input<Tasklist>();
  isTaskModalOpen = false;

  constructor(private fb: FormBuilder, private service: DashboardService) {
    this.newTaskFormGroup = this.fb.group({
      description: '',
      tasklistId: null,
    });
  }

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['tasklist'].currentValue) {
      this.newTaskFormGroup.get('tasklistId')?.setValue(changes['tasklist'].currentValue.id);
    }
  }

  createNewTask() {
    this.isTaskModalOpen = false;

    this.service.createNewTask(this.newTaskFormGroup.value).subscribe(() => {
      this.onTaskCreated.emit();
      this.newTaskFormGroup.reset();
    });
  }

  delete() {
    this.service.deleteTasklist(this.tasklist()!.id).subscribe(() => this.onTasklistDelete.emit());
  }
}
