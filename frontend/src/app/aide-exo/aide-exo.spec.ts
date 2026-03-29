import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AideExo } from './aide-exo';

describe('AideExo', () => {
  let component: AideExo;
  let fixture: ComponentFixture<AideExo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AideExo]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AideExo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
