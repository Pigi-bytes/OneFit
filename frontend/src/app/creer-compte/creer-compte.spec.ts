import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreerCompte } from './creer-compte';

describe('CreerCompte', () => {
  let component: CreerCompte;
  let fixture: ComponentFixture<CreerCompte>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreerCompte]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreerCompte);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
