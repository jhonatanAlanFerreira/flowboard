import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateWorkspaceWithAiComponent } from './create-workspace-with-ai-component';

describe('CreateWorkspaceWithAiComponent', () => {
  let component: CreateWorkspaceWithAiComponent;
  let fixture: ComponentFixture<CreateWorkspaceWithAiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateWorkspaceWithAiComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateWorkspaceWithAiComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
