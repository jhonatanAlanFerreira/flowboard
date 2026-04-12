import { TestBed } from '@angular/core/testing';

import { AiProcessingService } from './ai-processing-service';

describe('AiProcessingService', () => {
  let service: AiProcessingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AiProcessingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
