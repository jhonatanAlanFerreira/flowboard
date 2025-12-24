import { Component, EventEmitter, Output, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';

@Component({
  selector: 'app-dialog-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './dialog-component.html',
  styleUrl: './dialog-component.css',
})
export class DialogComponent {
  @Output() onConfirm = new EventEmitter();
  @Output() onCancel = new EventEmitter();

  confirmationControl = new FormControl<string | null>(null);

  header = input.required<string>();
  visible = input(false);
  inputValueConfirmation = input<string>();

  confirm() {}

  onHide() {
    this.confirmationControl.reset();
  }

  get isDisabled() {
    return (
      !!this.inputValueConfirmation() &&
      this.inputValueConfirmation()?.toLowerCase() !=
        this.confirmationControl.value?.toLowerCase()
    );
  }
}
