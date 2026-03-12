import { Directive, ElementRef, HostListener } from '@angular/core';

@Directive({
    selector: `[tooltip]`,
    standalone: true
})
export class TooltipMoveDirective {
    private tooltip?: HTMLElement;

    constructor(private host: ElementRef<HTMLElement>) {}

    @HostListener('mousemove', ['$event'])
    onMouseMove(event: MouseEvent): void {
        if (!this.tooltip) {
            this.tooltip = this.host.nativeElement.querySelector('.tooltiptext') as HTMLElement | null || undefined;
        }
        if (this.tooltip) {
            this.tooltip.style.left = (event.clientX + 10) + 'px';
            this.tooltip.style.top = (event.clientY + 10) + 'px';
        }
    }
}

