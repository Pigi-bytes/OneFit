import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HelpMenu } from './help-menu';

describe('HelpMenu', () => {
  let component: HelpMenu;
  let fixture: ComponentFixture<HelpMenu>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HelpMenu]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HelpMenu);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
