import { TestBed } from '@angular/core/testing';

import { DataQuestionService } from './data-question-service';

describe('DataQuestionService', () => {
  let service: DataQuestionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataQuestionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
