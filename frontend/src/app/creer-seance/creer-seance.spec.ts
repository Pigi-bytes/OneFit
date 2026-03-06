import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreerSeance } from './creer-seance';

describe('CreerSeance', () => {
  let component: CreerSeance;
  let fixture: ComponentFixture<CreerSeance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreerSeance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreerSeance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
