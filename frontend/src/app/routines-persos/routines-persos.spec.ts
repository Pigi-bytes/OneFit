import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoutinesPersos } from './routines-persos';

describe('RoutinesPersos', () => {
  let component: RoutinesPersos;
  let fixture: ComponentFixture<RoutinesPersos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoutinesPersos]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoutinesPersos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
