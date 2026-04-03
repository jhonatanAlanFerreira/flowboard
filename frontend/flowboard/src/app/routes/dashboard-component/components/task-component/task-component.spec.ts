import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TaskComponent } from './task-component';
import { TaskService } from '../../../../services/task/task-service';
import { of } from 'rxjs';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('TaskComponent', () => {
  let component: TaskComponent;
  let fixture: ComponentFixture<TaskComponent>;

  beforeEach(async () => {
    vi.useFakeTimers();

    await TestBed.configureTestingModule({
      imports: [TaskComponent],
      providers: [
        {
          provide: TaskService,
          useValue: { update: vi.fn().mockReturnValue(of({})) },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TaskComponent);
    component = fixture.componentInstance;
    component.task = { id: 1, name: 'Test' } as any;
    fixture.detectChanges();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should handle contentCopied signal and timeout using Vitest timers', async () => {
    expect(component.contentCopied()).toBe(false);

    component.showCopied();
    expect(component.contentCopied()).toBe(true);

    vi.advanceTimersByTime(1500);

    expect(component.contentCopied()).toBe(false);
  });
});
