import { Component, EventEmitter, Output, forwardRef, input } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';

@Component({
  selector: 'app-dropdown-component',
  standalone: true,
  imports: [FormsModule, SelectModule, ButtonModule],
  templateUrl: './dropdown-component.html',
  styleUrl: './dropdown-component.css',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DropdownComponent),
      multi: true,
    },
  ],
})
export class DropdownComponent implements ControlValueAccessor {
  @Output() onAdd = new EventEmitter();
  options = input.required<any[]>();
  optionLabel = input.required<string>();
  placeholder = input.required<string>();
  addOption = input<boolean>(false);

  value: any;
  disabled = false;

  private onChange = (value: any) => {};
  private onTouched = () => {};

  writeValue(value: any): void {
    this.value = value;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  onValueChange(value: any) {
    this.value = value;
    this.onChange(value);
    this.onTouched();
  }
}
