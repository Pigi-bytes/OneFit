import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecapSceance } from './recap-sceance';

describe('RecapSceance', () => {
  let component: RecapSceance;
  let fixture: ComponentFixture<RecapSceance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecapSceance]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecapSceance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
