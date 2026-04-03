import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DialogComponent } from './dialog-component';
import { ReactiveFormsModule } from '@angular/forms';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('DialogComponent', () => {
  let component: DialogComponent;
  let fixture: ComponentFixture<DialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DialogComponent, ReactiveFormsModule],
    }).compileComponents();

    fixture = TestBed.createComponent(DialogComponent);
    component = fixture.componentInstance;

    fixture.componentRef.setInput('header', 'Test Header');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should reset the form control when onHide is called', () => {
    component.confirmationControl.setValue('some text');
    component.onHide();
    expect(component.confirmationControl.value).toBeNull();
  });

  describe('isDisabled logic', () => {
    it('should be disabled if inputValueConfirmation is set and does not match control value', () => {
      fixture.componentRef.setInput('inputValueConfirmation', 'DELETE');

      component.confirmationControl.setValue('DEL');
      fixture.detectChanges();

      expect(component.isDisabled).toBe(true);
    });

    it('should be enabled if control value matches inputValueConfirmation (case insensitive)', () => {
      fixture.componentRef.setInput('inputValueConfirmation', 'DELETE');

      component.confirmationControl.setValue('delete');
      fixture.detectChanges();

      expect(component.isDisabled).toBe(false);
    });

    it('should be enabled if no confirmation value is required', () => {
      fixture.componentRef.setInput('inputValueConfirmation', undefined);

      component.confirmationControl.setValue('');
      fixture.detectChanges();

      expect(component.isDisabled).toBe(false);
    });
  });

  it('should emit onCancel when cancel is triggered (if you add a cancel method)', () => {
    const spy = vi.spyOn(component.onCancel, 'emit');
    component.onCancel.emit();
    expect(spy).toHaveBeenCalled();
  });
});
