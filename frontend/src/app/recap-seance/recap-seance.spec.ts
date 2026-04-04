import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecapSeance } from './recap-seance';

describe('RecapSeance', () => {
  let component: RecapSeance;
  let fixture: ComponentFixture<RecapSeance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecapSeance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecapSeance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
