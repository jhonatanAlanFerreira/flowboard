import { Component, EventEmitter, Output, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';

@Component({
  selector: 'app-create-workspace-with-ai-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './create-workspace-with-ai-component.html',
  styleUrl: './create-workspace-with-ai-component.css',
})
export class CreateWorkspaceWithAiComponent {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter();

  descriptionControl = new FormControl();
  visible = input(false);

  constructor(private workspaceService: WorkspaceService) {}

  save() {}

  onHide() {
    this.descriptionControl.reset();
    this.onCancel.emit();
  }
}
