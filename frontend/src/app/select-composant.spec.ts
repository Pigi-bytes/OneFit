import { TestBed } from '@angular/core/testing';

import { SelectComposant } from './select-composant';

describe('SelectComposant', () => {
  let service: SelectComposant;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SelectComposant);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
