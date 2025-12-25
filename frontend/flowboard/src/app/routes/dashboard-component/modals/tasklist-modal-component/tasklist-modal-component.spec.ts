import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TasklistModalComponent } from './tasklist-modal-component';

describe('TasklistModalComponent', () => {
  let component: TasklistModalComponent;
  let fixture: ComponentFixture<TasklistModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TasklistModalComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TasklistModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
