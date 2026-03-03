import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Carte } from './carte';

describe('Carte', () => {
  let component: Carte;
  let fixture: ComponentFixture<Carte>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Carte]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Carte);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
