import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SendListToWorkspaceModalComponent } from './send-list-to-workspace-modal-component';

describe('SendListToWorkspaceModalComponent', () => {
  let component: SendListToWorkspaceModalComponent;
  let fixture: ComponentFixture<SendListToWorkspaceModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SendListToWorkspaceModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SendListToWorkspaceModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
