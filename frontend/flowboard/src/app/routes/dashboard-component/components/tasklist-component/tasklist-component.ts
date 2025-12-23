import { Component, EventEmitter, Output, input } from '@angular/core';
import { TaskComponent } from '../task-component/task-component';
import { Task, Tasklist } from '../../../../models';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { EditButtonComponent } from '../../../../components/edit-button-component/edit-button-component';
import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { Divider } from 'primeng/divider';

@Component({
  selector: 'app-tasklist-component',
  imports: [
    TaskComponent,
    ReactiveFormsModule,
    FormsModule,
    Button,
    EditButtonComponent,
    CdkDrag,
    CdkScrollable,
    CdkDropList,
    Divider,
  ],
  templateUrl: './tasklist-component.html',
  styleUrl: './tasklist-component.css',
})
export class TasklistComponent {
  @Output() onTaskCreated = new EventEmitter();
  @Output() onTaskDelete = new EventEmitter();
  @Output() onTasklistDelete = new EventEmitter();

  tasklist = input<Tasklist>();
  workspaceDeleting = input(false);

  onDropTask(event: CdkDragDrop<Task[] | undefined>) {
    if (!event.container.data || !event.previousContainer.data) {
      return;
    }

    if (event.previousContainer === event.container) {
      moveItemInArray(
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
    }

    // this.service
    //   .reorderTasks(
    //     this.tasklist()!.id,
    //     event.item.data.tasklist_id,
    //     event.container.data.map((t) => t.id),
    //   )
    //   .subscribe();
  }
}
