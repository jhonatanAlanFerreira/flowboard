import { Component, EventEmitter, OnChanges, Output, SimpleChange, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Tasklist } from '../../../../models';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DashboardService } from '../../dashboard-service';

@Component({
  selector: 'app-tasklist-component',
  imports: [TaskComponent, ReactiveFormsModule, FormsModule],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent implements OnChanges {
  @Output() onTaskCreated = new EventEmitter();
  newTaskFormGroup: FormGroup;
  tasklist = input<Tasklist>();

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
    this.service.createNewTask(this.newTaskFormGroup.value).subscribe(() => {
      this.onTaskCreated.emit();
      this.newTaskFormGroup.reset();
    });
  }
}
