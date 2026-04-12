import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataQuestionModalComponent } from './data-question-modal-component';

describe('DataQuestionModalComponent', () => {
  let component: DataQuestionModalComponent;
  let fixture: ComponentFixture<DataQuestionModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DataQuestionModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataQuestionModalComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
