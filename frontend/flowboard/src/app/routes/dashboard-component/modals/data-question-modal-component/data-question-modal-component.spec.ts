import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';
import { MessageService } from 'primeng/api';
import { DataQuestionModalComponent } from './data-question-modal-component';
import { DataQuestionService } from '../../../../services/data-question/data-question-service';
import { LoginService } from '../../../../services/login/login-service';
import { User, Task } from '../../../../models';

describe('DataQuestionModalComponent', () => {
  let component: DataQuestionModalComponent;
  let fixture: ComponentFixture<DataQuestionModalComponent>;

  const mockUser: User = { id: 1, name: 'Test User' } as User;

  const dataQuestionServiceMock = {
    doneAskAi$: of(null),
    askAI: vi.fn().mockReturnValue(of({})),
    setPendingAskAi: vi.fn(),
    startPolling: vi.fn(),
    hasPendingAskAi: vi.fn().mockReturnValue(false),
  };

  const loginServiceMock = {
    getUser: vi.fn().mockReturnValue(of(mockUser)),
  };

  const messageServiceMock = {
    add: vi.fn(),
  };

  beforeEach(async () => {
    dataQuestionServiceMock.doneAskAi$ = of(null);
    loginServiceMock.getUser.mockReturnValue(of(mockUser));

    await TestBed.configureTestingModule({
      imports: [DataQuestionModalComponent],
      providers: [
        { provide: DataQuestionService, useValue: dataQuestionServiceMock },
        { provide: LoginService, useValue: loginServiceMock },
        { provide: MessageService, useValue: messageServiceMock },
      ],
    })
      .overrideComponent(DataQuestionModalComponent, {
        set: {
          template: '',
          imports: [],
        },
      })
      .compileComponents();

    fixture = TestBed.createComponent(DataQuestionModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should subscribe to doneAskAi$ and populate answers on init', () => {
    const mockResponse = {
      answer: 'This is the answer',
      source_tasks: [{ id: '1', content: 'Task 1' } as any],
    };

    dataQuestionServiceMock.doneAskAi$ = of(mockResponse) as any;

    component.ngOnInit();

    expect(component.isAnswerReadyModal()).toBe(true);
    expect(component.markdownAnswer()).toBe('This is the answer');
    expect(component.sourceTasks()).toEqual(mockResponse.source_tasks);
  });

  it('should start polling if user has pending questions on init', () => {
    dataQuestionServiceMock.hasPendingAskAi.mockReturnValue(true);

    component.ngOnInit();

    expect(dataQuestionServiceMock.startPolling).toHaveBeenCalledWith(
      component.onPullingFailed,
      mockUser.id,
    );
  });

  it('should call askAI and trigger loading workflow on success', () => {
    const onCreateSpy = vi.spyOn(component.onCreate, 'emit');
    component.questionControl.setValue('What are my tasks?');

    component.ask();

    expect(dataQuestionServiceMock.askAI).toHaveBeenCalledWith({
      prompt: 'What are my tasks?',
    });
    expect(onCreateSpy).toHaveBeenCalled();
    expect(dataQuestionServiceMock.setPendingAskAi).toHaveBeenCalledWith(
      mockUser.id,
    );
    expect(messageServiceMock.add).toHaveBeenCalledWith(
      expect.objectContaining({ severity: 'success' }),
    );
  });

  it('should show error toast when askAI fails', () => {
    dataQuestionServiceMock.askAI.mockReturnValue(
      throwError(() => new Error('Error')),
    );
    component.questionControl.setValue('What are my tasks?');

    component.ask();

    expect(messageServiceMock.add).toHaveBeenCalledWith(
      expect.objectContaining({
        severity: 'error',
        summary: 'Failed to reach AI Assistant',
      }),
    );
  });

  it('should emit onTaskClicked with mapped workspace and close the modal', () => {
    const onTaskClickedSpy = vi.spyOn(component.onTaskClicked, 'emit');
    const mockTask = {
      description: 'Task Description',
      tasklist: {
        workspace: { id: 'ws_1', name: 'Dev Workspace' },
      },
    } as unknown as Task;

    component.isAnswerReadyModal.set(true);
    component.taskClicked(mockTask);

    expect(component.isAnswerReadyModal()).toBe(false);
    expect(onTaskClickedSpy).toHaveBeenCalledWith({
      workspace: mockTask.tasklist!.workspace,
      taskDescription: mockTask.description,
    });
  });

  it('should reset control and emit onCancel on hide', () => {
    const onCancelSpy = vi.spyOn(component.onCancel, 'emit');
    component.questionControl.setValue('Sample text');

    component.onHide();

    expect(component.questionControl.value).toBeNull();
    expect(onCancelSpy).toHaveBeenCalled();
  });
});
