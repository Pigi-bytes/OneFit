import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Chrono } from './chrono';

describe('Chrono', () => {
  let component: Chrono;
  let fixture: ComponentFixture<Chrono>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Chrono]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Chrono);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
