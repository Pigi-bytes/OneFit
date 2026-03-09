import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AjouterExo } from './ajouter-exo';

describe('CreerSeance', () => {
    let component: AjouterExo;
    let fixture: ComponentFixture<AjouterExo>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AjouterExo]
        })
            .compileComponents();

        fixture = TestBed.createComponent(AjouterExo);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
