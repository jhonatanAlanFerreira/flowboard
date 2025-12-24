import {
  Component,
  EventEmitter,
  OnChanges,
  Output,
  SimpleChange,
  input,
} from '@angular/core';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Workspace } from '../../../../models';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';

@Component({
  selector: 'app-workspace-modal-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './workspace-modal-component.html',
  styleUrl: './workspace-modal-component.css',
})
export class WorkspaceModalComponent implements OnChanges {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter<Workspace>();

  workspace = input<Workspace | null>(null);
  visible = input(false);

  nameControl = new FormControl<string>('');

  constructor(private workspaceService: WorkspaceService) {}

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['workspace']) {
      this.nameControl.setValue(this.workspace()?.name || '');
    }
  }

  save() {
    if (this.workspace()?.id) {
      this.workspaceService
        .update({ name: this.nameControl.value!, id: this.workspace()!.id })
        .subscribe((res) => {
          this.onSave.emit(res);
        });
    } else {
      this.workspaceService
        .create({ name: this.nameControl.value! })
        .subscribe((res) => {
          this.onSave.emit(res);
        });
    }
  }

  onHide() {
    this.nameControl.reset();
    this.onCancel.emit();
  }

  get header() {
    return this.workspace()?.id
      ? 'Update Workspace name'
      : 'Create new Workspace';
  }
}
