import { Directive, HostListener, Input } from '@angular/core';

@Directive({
    selector: `[tooltip]`,
    standalone: true
})
export class TooltipMoveDirective {
    @Input('tooltip') tooltip!: HTMLElement;

    @HostListener('mousemove', ['$event'])
    onMouseMove(event: MouseEvent): void {
        if (this.tooltip) {
            this.tooltip.style.left = (event.clientX + 10) + 'px';
            this.tooltip.style.top = (event.clientY + 10) + 'px';
        }
    }
}

