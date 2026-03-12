import { TooltipMoveDirective } from './tooltipmove';
import { ElementRef } from '@angular/core';

describe('TooltipMoveDirective', () => {
  it('should create an instance', () => {
    const dummyEl = document.createElement('div');
    const directive = new TooltipMoveDirective(new ElementRef(dummyEl));
    expect(directive).toBeTruthy();
  });
});
