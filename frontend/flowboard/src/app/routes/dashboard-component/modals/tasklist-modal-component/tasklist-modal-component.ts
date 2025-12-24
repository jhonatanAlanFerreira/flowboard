import {
  Component,
  EventEmitter,
  Output,
  SimpleChange,
  input,
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Tasklist } from '../../../../models';
import { TasklistService } from '../../../../services/tasklist/tasklist-service';

@Component({
  selector: 'app-tasklist-modal-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './tasklist-modal-component.html',
  styleUrl: './tasklist-modal-component.css',
})
export class TasklistModalComponent {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter();

  workspaceId = input.required<number | null>();
  tasklist = input<Tasklist | null>(null);
  visible = input(false);

  nameControl = new FormControl<string>('');

  constructor(private tasklistService: TasklistService) {}

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['tasklist']) {
      this.nameControl.setValue(this.tasklist()?.name || '');
    }
  }

  save() {
    if (this.tasklist()?.id) {
      this.tasklistService
        .update({
          name: this.nameControl.value!,
          id: this.tasklist()!.id,
          workspaceId: this.workspaceId()!,
        })
        .subscribe(() => {
          this.onSave.emit();
        });
    } else {
      this.tasklistService
        .create({
          name: this.nameControl.value!,
          workspaceId: this.workspaceId()!,
        })
        .subscribe(() => {
          this.onSave.emit();
        });
    }
  }

  onHide() {
    this.nameControl.reset();
    this.onCancel.emit();
  }

  get header() {
    return this.tasklist()?.id ? 'Update List name' : 'Create new List';
  }
}
