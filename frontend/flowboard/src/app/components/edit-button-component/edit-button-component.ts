import { Component, EventEmitter, Output } from '@angular/core';
import { Button } from 'primeng/button';
import { Menu } from 'primeng/menu';

@Component({
  selector: 'app-edit-button-component',
  imports: [Button, Menu],
  templateUrl: './edit-button-component.html',
  styleUrl: './edit-button-component.css',
})
export class EditButtonComponent {
  @Output() onEdit = new EventEmitter();
  @Output() onDelete = new EventEmitter();

  items = [
    {
      label: 'Edit',
      icon: 'pi pi-pencil',
      command: () => this.onEdit.emit(),
    },
    {
      label: 'Delete',
      icon: 'pi pi-trash',
      command: () => this.onDelete.emit(),
    },
  ];
}
