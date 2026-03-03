import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SendTaskToWorkspaceModalComponent } from './send-task-to-workspace-modal-component';

describe('SendTaskToWorkspaceModalComponent', () => {
  let component: SendTaskToWorkspaceModalComponent;
  let fixture: ComponentFixture<SendTaskToWorkspaceModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SendTaskToWorkspaceModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SendTaskToWorkspaceModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
