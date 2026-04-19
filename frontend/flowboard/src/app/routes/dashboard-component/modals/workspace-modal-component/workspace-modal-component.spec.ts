import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { vi } from 'vitest';
import { MessageService } from 'primeng/api';
import { WorkspaceModalComponent } from './workspace-modal-component';
import { WorkspaceService } from '../../../../services/workspace/workspace-service';
import { SimpleChange } from '@angular/core';

describe('WorkspaceModalComponent', () => {
  let component: WorkspaceModalComponent;
  let fixture: ComponentFixture<WorkspaceModalComponent>;

  const workspaceServiceMock = {
    listWorkflowCategories: vi.fn().mockReturnValue(of([])),
    create: vi.fn().mockReturnValue(of({ id: 1, name: 'New' })),
    update: vi.fn().mockReturnValue(of({ id: 1, name: 'Updated' })),
    createWorkflowCategorie: vi.fn().mockReturnValue(of({ id: 99, name: 'New Cat' })),
  };

  const messageServiceMock = {
    add: vi.fn(),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkspaceModalComponent],
      providers: [
        { provide: WorkspaceService, useValue: workspaceServiceMock },
        { provide: MessageService, useValue: messageServiceMock },
      ],
    })
      .overrideComponent(WorkspaceModalComponent, {
        set: {
          template: '',
          imports: [],
        },
      })
      .compileComponents();

    fixture = TestBed.createComponent(WorkspaceModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load categories on init', () => {
    expect(workspaceServiceMock.listWorkflowCategories).toHaveBeenCalled();
  });

  it('should update form controls when workspace input changes', () => {
    const mockWorkspace = { id: 1, name: 'Test Workspace', category: { id: 2, name: 'Tech' } } as any;

    (component as any).workspace = () => mockWorkspace;
    component.ngOnChanges({
      workspace: new SimpleChange(null, mockWorkspace, false)
    });

    expect(component.nameControl.value).toBe('Test Workspace');
    expect(component.categoryControl.value).toEqual(mockWorkspace.category);
  });

  it('should call create when saving a new workspace (no id)', () => {
    const saveSpy = vi.spyOn(component.onSave, 'emit');
    component.nameControl.setValue('New App');
    component.categoryControl.setValue({ id: 5, name: 'Cat' });

    component.save();

    expect(workspaceServiceMock.create).toHaveBeenCalledWith({
      name: 'New App',
      workspace_category_id: 5
    });
    expect(saveSpy).toHaveBeenCalled();
  });

  it('should call update when saving an existing workspace', () => {
    const mockWorkspace = { id: 10, name: 'Old' } as any;
    (component as any).workspace = () => mockWorkspace;

    component.nameControl.setValue('Updated Name');
    component.categoryControl.setValue({ id: 5, name: 'Cat' });

    component.save();

    expect(workspaceServiceMock.update).toHaveBeenCalledWith({
      id: 10,
      name: 'Updated Name',
      workspace_category_id: 5
    });
  });

  it('should show error message if adding a category without a name', () => {
    component.onAddWorkspaceCategory(null);
    expect(messageServiceMock.add).toHaveBeenCalledWith(expect.objectContaining({
      severity: 'error'
    }));
  });

  it('should create a new category and refresh the list', () => {
    component.onAddWorkspaceCategory('New Category');

    expect(workspaceServiceMock.createWorkflowCategorie).toHaveBeenCalledWith({
      name: 'New Category',
      id: null
    });
    expect(component.categoryControl.value).toEqual({ id: 99, name: 'New Cat' });
  });

  it('should reset form and emit cancel onHide', () => {
    const cancelSpy = vi.spyOn(component.onCancel, 'emit');
    component.nameControl.setValue('Dirty Value');

    component.onHide();

    expect(component.nameControl.value).toBe(null);
    expect(cancelSpy).toHaveBeenCalled();
  });
});
