import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModifPassword } from './modif-password';

describe('ModifPassword', () => {
  let component: ModifPassword;
  let fixture: ComponentFixture<ModifPassword>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModifPassword]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModifPassword);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
