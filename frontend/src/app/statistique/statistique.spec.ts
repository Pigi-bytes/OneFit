import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Statistique } from './statistique';

describe('Statistique', () => {
  let component: Statistique;
  let fixture: ComponentFixture<Statistique>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Statistique]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Statistique);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
