import { NgClass } from '@angular/common';
import {
  Component,
  EventEmitter,
  input,
  OnDestroy,
  OnInit,
  Output,
  signal,
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Subject, takeUntil } from 'rxjs';
import { LoginService } from '../../../../services/login/login-service';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';
import { User } from '../../../../models';
import { AiProcessingService } from '../../../../services/ai-processing-service';

@Component({
  selector: 'app-data-question-modal-component',
  imports: [NgClass, Dialog, Button, ReactiveFormsModule],
  templateUrl: './data-question-modal-component.html',
  styleUrl: './data-question-modal-component.css',
})
export class DataQuestionModalComponent implements OnInit, OnDestroy {
  @Output() onCancel = new EventEmitter();
  @Output() onCreate = new EventEmitter();
  @Output() onSave = new EventEmitter();

  visible = input(false);

  private destroy$ = new Subject<void>();

  questionControl = new FormControl();
  isAnswerReadyModal = signal(false);
  markdownAnswer = signal("");
  sourceTasks = signal<any[]>([]);

  user: User | null = null;

  constructor(
    private workspaceService: WorkspaceService,
    private messageService: MessageService,
    private loginService: LoginService,
    private aiProcessingService: AiProcessingService,
  ) {}

  ngOnInit(): void {
    this.workspaceService.doneWorkspace$
      .pipe(takeUntil(this.destroy$))
      .subscribe((res) => {
        if (!res) return;

        this.isAnswerReadyModal.set(true);

        this.markdownAnswer.set(res.answer);
        this.sourceTasks.set(res.source_tasks);
      });

    this.loginService
      .getUser()
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        this.user = user;

        if (!user) return;

        if (this.isProcessing) {
          this.workspaceService.startPolling(this.onPullingFailed, user.id);
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ask() {
    if (!this.user) return;

    this.aiProcessingService
      .askAI({
        prompt: this.questionControl.value,
      })
      .subscribe({
        next: () => {
          this.onCreate.emit();

          this.workspaceService.setPendingWorkspace(this.user!.id);
          this.workspaceService.startPolling(
            this.onPullingFailed,
            this.user!.id,
          );

          this.messageService.add({
            severity: 'success',
            summary: 'AI Assistant is on it!',
            detail:
              'We are searching your workspaces. You will be notified as soon as your answer is generated.',
            sticky: true,
            closable: true,
          });
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Failed to reach AI Assistant',
            detail: 'Please try again in a few moments.',
            sticky: true,
            closable: true,
          });
        },
      });
  }

  onHide() {
    this.questionControl.reset();
    this.onCancel.emit();
  }

  onPullingFailed = () => {
    this.messageService.add({
      severity: 'error',
      summary: 'AI Assistant couldn’t answer that',
      detail:
        'We couldn’t find a clear answer in your current tasks. This may happen if the question is too vague or refers to documents outside your boards. Please try rephrasing your question or adding more specific details about the task you are looking for.',
      sticky: true,
      closable: true,
    });
  };

  get isProcessing() {
    return this.user
      ? this.workspaceService.hasPendingWorkspace(this.user.id)
      : false;
  }
}
