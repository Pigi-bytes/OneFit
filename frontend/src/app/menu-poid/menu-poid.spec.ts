import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MenuPoid } from './menu-poid';

describe('MenuPoid', () => {
  let component: MenuPoid;
  let fixture: ComponentFixture<MenuPoid>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MenuPoid]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MenuPoid);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
