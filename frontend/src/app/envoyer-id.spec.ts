import { TestBed } from '@angular/core/testing';

import { EnvoyerId } from './envoyer-id';

describe('EnvoyerId', () => {
  let service: EnvoyerId;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EnvoyerId);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
