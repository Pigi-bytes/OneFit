import { TestBed } from '@angular/core/testing';

import { EnvoyerElt } from './envoyer-id';

describe('EnvoyerElt', () => {
    let service: EnvoyerElt;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(EnvoyerElt);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
