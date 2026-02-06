import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurerCompte } from './configurer-compte';

describe('ConfigurerCompte', () => {
  let component: ConfigurerCompte;
  let fixture: ComponentFixture<ConfigurerCompte>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfigurerCompte]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfigurerCompte);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
