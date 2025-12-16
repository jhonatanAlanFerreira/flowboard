import { Component } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';

@Component({
  selector: 'app-taskscolumn-component',
  imports: [TaskComponent],
  templateUrl: './taskscolumn-component.html',
  styleUrl: './taskscolumn-component.css',
})
export class TaskscolumnComponent {}
