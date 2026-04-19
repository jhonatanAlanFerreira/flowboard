import {
  Component,
  EventEmitter,
  OnChanges,
  OnInit,
  Output,
  SimpleChange,
  input,
  signal,
} from '@angular/core';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Category, Workspace } from '../../../../models';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';
import { DropdownComponent } from '../../../../components/dropdown-component/dropdown-component';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-workspace-modal-component',
  imports: [Dialog, Button, ReactiveFormsModule, DropdownComponent],
  templateUrl: './workspace-modal-component.html',
  styleUrl: './workspace-modal-component.css',
})
export class WorkspaceModalComponent implements OnChanges, OnInit {
  @Output() onCancel = new EventEmitter();
  @Output() onSave = new EventEmitter<Workspace>();

  workspace = input<Workspace | null>(null);
  visible = input(false);

  categories = signal<Category[]>([]);
  loading = signal(false);

  nameControl = new FormControl<string>('');
  categoryControl = new FormControl<Category | null>(null);

  constructor(
    private workspaceService: WorkspaceService,
    private messageService: MessageService,
  ) {}

  ngOnInit(): void {
    this.listWorkflowCategories();
  }

  ngOnChanges(changes: { [propName: string]: SimpleChange<any> }): void {
    if (changes['workspace']) {
      this.nameControl.setValue(this.workspace()?.name || '');
      this.categoryControl.setValue(
        this.workspace()?.category || { name: 'Uncategorized', id: null },
      );
    }
  }

  save() {
    if (this.workspace()?.id) {
      this.workspaceService
        .update({
          name: this.nameControl.value!,
          id: this.workspace()!.id,
          workspace_category_id: this.categoryControl.value!.id!,
        })
        .subscribe((res) => {
          this.onSave.emit(res);
        });
    } else {
      this.workspaceService
        .create({
          name: this.nameControl.value!,
          workspace_category_id: this.categoryControl.value?.id || null,
        })
        .subscribe((res) => {
          this.onSave.emit(res);
        });
    }
  }

  onHide() {
    this.nameControl.reset();
    this.onCancel.emit();
  }

  listWorkflowCategories() {
    this.loading.set(true);

    this.workspaceService.listWorkflowCategories().subscribe((categories) => {
      this.categories.set(categories);
      this.loading.set(false);
    });
  }

  onAddWorkspaceCategory(newCategoryName: string | null) {
    if (!newCategoryName) {
      return this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Enter the name of your new category.',
      });
    }

    this.loading.set(true);
    this.workspaceService
      .createWorkflowCategorie({ name: newCategoryName, id: null })
      .subscribe((category) => {
        this.categoryControl.setValue(category);
        this.listWorkflowCategories();
      });
  }

  get header() {
    return this.workspace()?.id
      ? 'Update Workspace name'
      : 'Create new Workspace';
  }

  get categoryOptions() {
    return [{ name: 'Uncategorized', id: null }, ...this.categories()];
  }
}
