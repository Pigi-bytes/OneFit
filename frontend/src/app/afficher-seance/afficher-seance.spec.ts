import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AfficheSeance } from './afficher-seance';

describe('AfficheSeance', () => {
  let component: AfficheSeance;
  let fixture: ComponentFixture<AfficheSeance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AfficheSeance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AfficheSeance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
