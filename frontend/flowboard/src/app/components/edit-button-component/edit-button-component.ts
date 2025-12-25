import {
  Component,
  EventEmitter,
  OnChanges,
  OnInit,
  Output,
  input,
} from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Button } from 'primeng/button';
import { Menu } from 'primeng/menu';

@Component({
  selector: 'app-edit-button-component',
  imports: [Button, Menu],
  templateUrl: './edit-button-component.html',
  styleUrl: './edit-button-component.css',
})
export class EditButtonComponent implements OnInit, OnChanges {
  @Output() onEdit = new EventEmitter();
  @Output() onDelete = new EventEmitter();
  @Output() onSortAsc = new EventEmitter();
  @Output() onSortDesc = new EventEmitter();

  sortAscLabel = input<string>();
  sortDescLabel = input<string>();

  items: MenuItem[] = [];

  ngOnInit(): void {
    this.buildItems();
  }

  ngOnChanges(): void {
    this.buildItems();
  }

  buildItems() {
    this.items = [
      ...(this.sortDescLabel()
        ? [
            {
              label: this.sortDescLabel(),
              labelClass: 'text-nowrap',
              icon: 'pi pi-sort-amount-up',
              command: () => this.onSortDesc.emit(),
            },
          ]
        : []),
      ...(this.sortAscLabel()
        ? [
            {
              label: this.sortAscLabel(),
              labelClass: 'text-nowrap',
              icon: 'pi pi-sort-amount-down',
              command: () => this.onSortAsc.emit(),
            },
          ]
        : []),
      {
        label: 'Edit',
        icon: 'pi pi-pencil',
        command: () => this.onEdit.emit(),
      },
      {
        label: 'Delete',
        icon: 'pi pi-trash',
        iconClass: 'text-red-500',
        labelClass: 'text-red-500',
        command: () => this.onDelete.emit(),
      },
    ];
  }
}
