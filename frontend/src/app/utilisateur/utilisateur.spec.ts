import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Utilisateur } from './utilisateur';

describe('Utilisateur', () => {
  let component: Utilisateur;
  let fixture: ComponentFixture<Utilisateur>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Utilisateur]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Utilisateur);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
