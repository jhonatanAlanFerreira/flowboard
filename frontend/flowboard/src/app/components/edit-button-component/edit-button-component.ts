import { Component, OnInit, input } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Button } from 'primeng/button';
import { Menu } from 'primeng/menu';

@Component({
  selector: 'app-edit-button-component',
  imports: [Button, Menu],
  templateUrl: './edit-button-component.html',
  styleUrl: './edit-button-component.css',
})
export class EditButtonComponent implements OnInit {
  items = input.required<MenuItem[]>();

  ngOnInit(): void {}
}
