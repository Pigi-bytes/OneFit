import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AfficheSceance } from './afficher-seance';

describe('AfficheSceance', () => {
  let component: AfficheSceance;
  let fixture: ComponentFixture<AfficheSceance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AfficheSceance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AfficheSceance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
