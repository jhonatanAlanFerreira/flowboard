import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EditButtonComponent } from './edit-button-component';
import { MenuItem } from 'primeng/api';
import { describe, it, expect, beforeEach } from 'vitest';

describe('EditButtonComponent', () => {
  let component: EditButtonComponent;
  let fixture: ComponentFixture<EditButtonComponent>;

  const mockItems: MenuItem[] = [
    { label: 'Edit', icon: 'pi pi-pencil' },
    { label: 'Delete', icon: 'pi pi-trash' },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditButtonComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EditButtonComponent);
    component = fixture.componentInstance;

    fixture.componentRef.setInput('items', mockItems);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should receive the items input correctly', () => {
    expect(component.items()).toEqual(mockItems);
    expect(component.items().length).toBe(2);
  });

  it('should have the first item label as "Edit"', () => {
    expect(component.items()[0].label).toBe('Edit');
  });
});
