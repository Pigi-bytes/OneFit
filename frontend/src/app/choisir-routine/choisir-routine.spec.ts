import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChoisirRoutine } from './choisir-routine';

describe('ChoisirRoutine', () => {
  let component: ChoisirRoutine;
  let fixture: ComponentFixture<ChoisirRoutine>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChoisirRoutine]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChoisirRoutine);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
