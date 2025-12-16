import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaskscolumnComponent } from './taskscolumn-component';

describe('TaskscolumnComponent', () => {
  let component: TaskscolumnComponent;
  let fixture: ComponentFixture<TaskscolumnComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaskscolumnComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TaskscolumnComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
