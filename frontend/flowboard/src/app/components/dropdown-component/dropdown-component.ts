import { Component, input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';

@Component({
  selector: 'app-dropdown-component',
  imports: [FormsModule, SelectModule, ButtonModule],
  templateUrl: './dropdown-component.html',
  styleUrl: './dropdown-component.css',
})
export class DropdownComponent {
  value: any;
  options = input.required<any[]>();
  optionLabel = input.required<string>();
  placeholder = input.required<string>();
}
