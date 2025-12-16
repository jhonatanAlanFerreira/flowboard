import { Component, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Tasklist } from '../../../../models';

@Component({
  selector: 'app-tasklist-component',
  imports: [TaskComponent],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent {
  tasklist = input<Tasklist>();
}
