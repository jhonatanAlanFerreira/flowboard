import { Component, EventEmitter, Output, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Workspace } from '../../../../models';
import { DropdownComponent } from '../../../../components/dropdown-component/dropdown-component';

@Component({
  selector: 'app-send-list-to-workspace-modal-component',
  imports: [Dialog, Button, ReactiveFormsModule, DropdownComponent],
  templateUrl: './send-list-to-workspace-modal-component.html',
  styleUrl: './send-list-to-workspace-modal-component.css',
})
export class SendListToWorkspaceModalComponent {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter<Workspace>();

  workspaces = input<Workspace[]>([]);
  visible = input(false);
  workspaceFrom = input.required<Workspace>();

  workspaceControl = new FormControl<Workspace | null>(null);

  save() {
    this.onSave.emit(this.workspaceControl.value!);
  }

  onHide() {
    this.workspaceControl.reset();
    this.onCancel.emit();
  }

  get workspaceOptions() {
    return this.workspaces().filter((ws) => ws.id != this.workspaceFrom().id);
  }
}
