import { TestBed } from '@angular/core/testing';

import { Erreur } from './erreur';

describe('Erreur', () => {
  let service: Erreur;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Erreur);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
