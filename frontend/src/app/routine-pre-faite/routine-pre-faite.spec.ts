import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoutinePreFaite } from './routine-pre-faite';

describe('RoutinePreFaite', () => {
  let component: RoutinePreFaite;
  let fixture: ComponentFixture<RoutinePreFaite>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoutinePreFaite]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoutinePreFaite);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
