import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Exercices } from './exercices';

describe('Exercices', () => {
  let component: Exercices;
  let fixture: ComponentFixture<Exercices>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Exercices]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Exercices);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
