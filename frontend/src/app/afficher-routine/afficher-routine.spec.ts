import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AfficherRoutine } from './afficher-routine';

describe('AfficherRoutine', () => {
  let component: AfficherRoutine;
  let fixture: ComponentFixture<AfficherRoutine>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AfficherRoutine]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AfficherRoutine);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
