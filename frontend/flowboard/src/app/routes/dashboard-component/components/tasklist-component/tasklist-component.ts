import { Component } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';

@Component({
  selector: 'app-tasklist-component',
  imports: [TaskComponent],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent {}
