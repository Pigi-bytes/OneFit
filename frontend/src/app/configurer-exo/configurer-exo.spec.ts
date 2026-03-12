import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurerExo } from './configurer-exo';

describe('ConfigurerExo', () => {
    let component: ConfigurerExo;
    let fixture: ComponentFixture<ConfigurerExo>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ConfigurerExo]
        })
            .compileComponents();

        fixture = TestBed.createComponent(ConfigurerExo);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
