import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SeanceEnCours } from './seance-en-cours';

describe('SeanceEnCours', () => {
  let component: SeanceEnCours;
  let fixture: ComponentFixture<SeanceEnCours>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SeanceEnCours]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SeanceEnCours);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
