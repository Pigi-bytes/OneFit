import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GraphPoid } from './graph-poid';

describe('GraphPoid', () => {
  let component: GraphPoid;
  let fixture: ComponentFixture<GraphPoid>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GraphPoid]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GraphPoid);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
