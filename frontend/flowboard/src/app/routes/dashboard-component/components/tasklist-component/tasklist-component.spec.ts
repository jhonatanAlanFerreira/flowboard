import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TasklistComponent } from './tasklist-component';
import { TasklistService } from '../../../../services/tasklist/tasklist-service';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { of } from 'rxjs';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { Task } from '../../../../models';

describe('TasklistComponent', () => {
  let component: TasklistComponent;
  let fixture: ComponentFixture<TasklistComponent>;

  const tasklistServiceMock = {
    delete: vi.fn().mockReturnValue(of({})),
    reorderTasks: vi.fn().mockReturnValue(of({})),
    updateTasklist: vi.fn().mockReturnValue(of({})),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TasklistComponent],
      providers: [{ provide: TasklistService, useValue: tasklistServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(TasklistComponent);
    component = fixture.componentInstance;

    fixture.componentRef.setInput('tasklist', { id: 100, tasks: [] });
    fixture.detectChanges();
  });

  it('should delete a tasklist using the signal value', () => {
    component.deleteTasklist();
    expect(tasklistServiceMock.delete).not.toHaveBeenCalled();
    const emitSpy = vi.spyOn(component.onTasklistDelete, 'emit');
    component.deleteTasklist();
    expect(emitSpy).toHaveBeenCalledWith({ tasklistId: 100 });
  });

  it('should reorder tasks within the same list', () => {
    const tasks: Task[] = [
      { id: 1, tasklist_id: 100 },
      { id: 2, tasklist_id: 100 },
    ] as any;

    const mockDropEvent = {
      previousIndex: 0,
      currentIndex: 1,
      container: { data: tasks },
      previousContainer: { data: tasks },
      item: { data: tasks[0] },
    } as CdkDragDrop<Task[] | undefined>;

    component.onDropTask(mockDropEvent);

    expect(tasklistServiceMock.reorderTasks).toHaveBeenCalledWith(
      100,
      100,
      [2, 1],
      null,
      1,
    );
  });

  it('should transfer tasks between different lists', () => {
    const sourceTasks: Task[] = [{ id: 1, tasklist_id: 100 }] as any;
    const targetTasks: Task[] = [{ id: 2, tasklist_id: 200 }] as any;

    const mockDropEvent = {
      previousIndex: 0,
      currentIndex: 1,
      previousContainer: { data: sourceTasks },
      container: { data: targetTasks },
      item: { data: sourceTasks[0] },
    } as CdkDragDrop<Task[] | undefined>;

    component.onDropTask(mockDropEvent);

    expect(targetTasks.length).toBe(2);
    expect(targetTasks[1].id).toBe(1);
    expect(tasklistServiceMock.reorderTasks).toHaveBeenCalled();
  });
});
