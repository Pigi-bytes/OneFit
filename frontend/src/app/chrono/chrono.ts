import { Component, OnInit, OnDestroy, Input, PLATFORM_ID, inject, AfterViewInit } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt';

@Component({
    selector: 'app-chrono',
    templateUrl: './chrono.html',
    styleUrl: './chrono.css',
})
export class Chrono implements OnInit, AfterViewInit, OnDestroy {

    @Input() isRunning: boolean = true;
    private platformId = inject(PLATFORM_ID);
    private subscription?: Subscription;

    constructor(private elt: EnvoyerElt) { }

    heure = 0;
    minute = 0;
    seconde = 0;
    temps: string = "00:00:00";

    private intervalId: any;

    ngOnInit() {
        this.subscription = this.elt.afficheExercice$.subscribe((id) => {
            if (id[0] === Message.RESET_CHRONO) {
                this.isRunning = false;
                this.resetChrono();
                return;
            }
        });
        if (isPlatformBrowser(this.platformId)) {
            const savedTime = localStorage.getItem("chronoTemps");
            if (savedTime) {
                [this.heure, this.minute, this.seconde] = savedTime.split(':').map(Number);
                this.updateTemps();
            }
        }
    }
    ngAfterViewInit() {
        if (isPlatformBrowser(this.platformId) && this.isRunning) {
            this.startChrono();
        }
    }

    ngOnDestroy() {
        this.stopChrono();
    }

    private startChrono() {
        if (!isPlatformBrowser(this.platformId)) return;
        if (!this.intervalId) {
            this.intervalId = setInterval(() => this.tick(), 1000);
        }
    }

    private stopChrono() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    private tick() {
        this.seconde++;
        if (this.seconde >= 60) { this.seconde = 0; this.minute++; }
        if (this.minute >= 60) { this.minute = 0; this.heure++; }

        this.updateTemps();

        if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem("chronoTemps", this.temps);
        }
    }

    private updateTemps() {
        this.temps = [this.heure, this.minute, this.seconde]
            .map(v => String(v).padStart(2, '0'))
            .join(':');
    }

    private resetChrono() {
        localStorage.removeItem("chronoTemps");
    }
}