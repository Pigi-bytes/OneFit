import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExerciceEnCours } from './exercice-en-cours';

describe('ExerciceEnCours', () => {
  let component: ExerciceEnCours;
  let fixture: ComponentFixture<ExerciceEnCours>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExerciceEnCours]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExerciceEnCours);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
