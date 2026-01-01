import {
  Component,
  EventEmitter,
  OnInit,
  Output,
  input,
  signal,
  OnDestroy,
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';
import { MessageService } from 'primeng/api';
import { User, Workspace } from '../../../../models';
import { LoginService } from '../../../../services/login/login-service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-create-workspace-with-ai-component',
  imports: [Dialog, Button, ReactiveFormsModule],
  templateUrl: './create-workspace-with-ai-component.html',
  styleUrl: './create-workspace-with-ai-component.css',
})
export class CreateWorkspaceWithAiComponent implements OnInit, OnDestroy {
  @Output() onCancel = new EventEmitter();
  @Output() onCreate = new EventEmitter();
  @Output() onSave = new EventEmitter();
  @Output() onWorkspaceClick = new EventEmitter<{
    workspace: Workspace;
    goToWorkspace: boolean;
  }>();

  private destroy$ = new Subject<void>();

  user: User | null = null;
  generatedWorkspace: Workspace | null = null;
  descriptionControl = new FormControl();

  workspaceDoneModal = signal(false);
  visible = input(false);

  constructor(
    private workspaceService: WorkspaceService,
    private messageService: MessageService,
    private loginService: LoginService,
  ) {}

  ngOnInit(): void {
    this.workspaceService.doneWorkspace$
      .pipe(takeUntil(this.destroy$))
      .subscribe((workspace) => {
        if (!workspace) return;

        this.generatedWorkspace = workspace;
        this.workspaceDoneModal.set(true);
      });

    this.loginService
      .getUser()
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        this.user = user;

        if (!user) return;

        if (this.workspaceService.hasPendingWorkspace(user.id)) {
          this.workspaceService.startPolling(this.onPullingFailed, user.id);
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  save() {
    if (!this.user) return;

    this.workspaceService
      .createByAI({ prompt: this.descriptionControl.value })
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
            summary: 'Workspace generation started',
            detail:
              'We’ll notify you when it’s ready. You can continue using the app while your workspace is being created.',
            sticky: true,
            closable: true,
          });
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Failed to start workspace generation',
            detail: 'Please try again.',
            sticky: true,
            closable: true,
          });
        },
      });
  }

  onHide() {
    this.descriptionControl.reset();
    this.onCancel.emit();
  }

  goToWorkspace() {
    this.workspaceDoneModal.set(false);
    this.workspaceService.clearDoneWorkspace();

    this.onWorkspaceClick.emit({
      workspace: this.generatedWorkspace!,
      goToWorkspace: true,
    });
  }

  onWorkspaceCreatedHide() {
    this.workspaceDoneModal.set(false);
    this.workspaceService.clearDoneWorkspace();

    this.onWorkspaceClick.emit({
      workspace: this.generatedWorkspace!,
      goToWorkspace: false,
    });
  }

  onPullingFailed = () => {
    this.messageService.add({
      severity: 'error',
      summary: 'Failed to create the workspace by AI',
      detail:
        'The workspace could not be generated. This may happen if the description doesn’t include enough context, or if it contains content that isn’t allowed. Please add more details about your project and make sure the description follows acceptable use guidelines, then try again.',
      sticky: true,
      closable: true,
    });
  };

  get header() {
    return `Your workspace "${this.generatedWorkspace?.name}" is ready`;
  }
}
