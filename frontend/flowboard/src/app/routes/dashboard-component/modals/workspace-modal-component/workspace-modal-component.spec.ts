import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkspaceModalComponent } from './workspace-modal-component';

describe('WorkspaceModalComponent', () => {
  let component: WorkspaceModalComponent;
  let fixture: ComponentFixture<WorkspaceModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkspaceModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WorkspaceModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
