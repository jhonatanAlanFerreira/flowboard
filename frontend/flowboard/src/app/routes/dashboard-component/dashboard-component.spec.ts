import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardComponent } from './dashboard-component';
import { of } from 'rxjs';
import { vi } from 'vitest';
import { MessageService } from 'primeng/api';
import { WorkspaceService } from '../../services/workspace/workspace-service';
import { TasklistService } from '../../services/tasklist/tasklist-service';
import { TaskService } from '../../services/task/task-service';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  const workspaceServiceMock = {
    list: vi.fn().mockReturnValue(of([])),
    delete: vi.fn().mockReturnValue(of({})),
    reorderTasklists: vi.fn().mockReturnValue(of({})),
    exportWorkspace: vi.fn(),
    checkAiEndpoint: vi.fn().mockReturnValue(of(true)),
  };

  const tasklistServiceMock = {
    listFromWorkspace: vi.fn().mockReturnValue(of([])),
    delete: vi.fn().mockReturnValue(of({})),
    copyList: vi.fn().mockReturnValue(of({})),
  };

  const taskServiceMock = {
    delete: vi.fn().mockReturnValue(of({})),
    sendTask: vi.fn().mockReturnValue(of({})),
  };

  const messageServiceMock = {
    add: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [
        { provide: WorkspaceService, useValue: workspaceServiceMock },
        { provide: TasklistService, useValue: tasklistServiceMock },
        { provide: TaskService, useValue: taskServiceMock },
        { provide: MessageService, useValue: messageServiceMock },
      ],
    })
      .overrideComponent(DashboardComponent, {
        set: {
          template: '',
          imports: [],
        },
      })
      .compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load workspaces on init', () => {
    component.ngOnInit();
    expect(workspaceServiceMock.list).toHaveBeenCalled();
  });

  it('should apply search correctly', () => {
    component.tasklists.set([
      {
        id: 1,
        tasks: [{ description: 'Test task', matchesSearch: false }],
      } as any,
    ]);

    component.searchControl.setValue('test');
    component.applySearch();

    const task = component.tasklists()[0].tasks![0];
    expect(task.matchesSearch).toBe(true);
  });

  it('should open AI modal when endpoint is available', () => {
    component.onAiAddWorkspace();
    expect(component.isCreateWorkspaceWithAiModalOpen()).toBe(true);
  });
});
