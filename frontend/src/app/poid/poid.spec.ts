import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Poid } from './poid';

describe('Poid', () => {
  let component: Poid;
  let fixture: ComponentFixture<Poid>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Poid]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Poid);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
