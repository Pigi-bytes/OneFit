import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModifeExercice } from './modife-exercice';

describe('ModifeExercice', () => {
  let component: ModifeExercice;
  let fixture: ComponentFixture<ModifeExercice>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModifeExercice]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModifeExercice);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
