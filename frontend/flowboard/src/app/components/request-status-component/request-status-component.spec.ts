import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestStatusComponent } from './request-status-component';

describe('RequestStatusComponent', () => {
  let component: RequestStatusComponent;
  let fixture: ComponentFixture<RequestStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RequestStatusComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RequestStatusComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
