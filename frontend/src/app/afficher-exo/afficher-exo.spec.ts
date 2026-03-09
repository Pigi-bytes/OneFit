import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AfficherExo } from './afficher-exo';

describe('AfficherExo', () => {
  let component: AfficherExo;
  let fixture: ComponentFixture<AfficherExo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AfficherExo]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AfficherExo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
