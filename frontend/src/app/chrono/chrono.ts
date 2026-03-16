import { Component } from '@angular/core';
import { ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-chrono',
    imports: [],
    templateUrl: './chrono.html',
    styleUrl: './chrono.css',
})
export class Chrono {

    constructor(private cdr: ChangeDetectorRef) { }

    seconde = 0;
    minute = 0;
    heure = 0;

    temps = "00:00:00";

    lanceChrono() {
        setInterval(() => this.chrono(), 1000);
    }

    chrono() {
        this.seconde++;
        if (this.seconde === 60) {
            this.minute++;
            this.seconde = 0;
        }
        if (this.minute === 60) {
            this.heure++;
            this.minute = 0;
        }
        this.temps = String(this.heure).padStart(2, "0") + ":" +
            String(this.minute).padStart(2, "0") + ":" +
            String(this.seconde).padStart(2, "0");
        this.cdr.detectChanges();
    }


}
