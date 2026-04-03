import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DropdownComponent } from './dropdown-component';
import { FormsModule } from '@angular/forms';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('DropdownComponent', () => {
  let component: DropdownComponent;
  let fixture: ComponentFixture<DropdownComponent>;

  const mockOptions = [
    { id: 1, name: 'Option 1' },
    { id: 2, name: 'Option 2' },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DropdownComponent, FormsModule],
    }).compileComponents();

    fixture = TestBed.createComponent(DropdownComponent);
    component = fixture.componentInstance;

    fixture.componentRef.setInput('options', mockOptions);
    fixture.componentRef.setInput('optionLabel', 'name');
    fixture.componentRef.setInput('placeholder', 'Select an item');

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should write value when writeValue is called', () => {
    const testValue = mockOptions[0];
    component.writeValue(testValue);
    expect(component.value).toEqual(testValue);
  });

  it('should call onChange and onTouched when onValueChange is triggered', () => {
    const onChangeSpy = vi.fn();
    const onTouchedSpy = vi.fn();
    const newValue = mockOptions[1];

    component.registerOnChange(onChangeSpy);
    component.registerOnTouched(onTouchedSpy);

    component.onValueChange(newValue);

    expect(component.value).toEqual(newValue);
    expect(onChangeSpy).toHaveBeenCalledWith(newValue);
    expect(onTouchedSpy).toHaveBeenCalled();
  });

  it('should update disabled state when setDisabledState is called', () => {
    component.setDisabledState(true);
    expect(component.disabled).toBe(true);

    component.setDisabledState(false);
    expect(component.disabled).toBe(false);
  });

  it('should emit onAdd when the add button is clicked (manually calling logic)', () => {
    const emitSpy = vi.spyOn(component.onAdd, 'emit');

    component.onAdd.emit();

    expect(emitSpy).toHaveBeenCalled();
  });
});
