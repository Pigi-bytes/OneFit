import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Seance } from './seance';

describe('Seance', () => {
  let component: Seance;
  let fixture: ComponentFixture<Seance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Seance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Seance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
