import { Component, Inject, inject, PLATFORM_ID } from '@angular/core';
import { CommonModule } from '@angular/common';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { AfficheSceance } from '../afficher-seance/afficher-seance';
import { Chrono } from '../chrono/chrono';

@Component({
    selector: 'app-seance-en-cours',
    imports: [Chrono, AfficheSceance],
    templateUrl: './seance-en-cours.html',
    styleUrl: './seance-en-cours.css',
})
export class SeanceEnCours {

    constructor(private router: Router) { }
    private platformId = inject(PLATFORM_ID);


    ngOnInit() {
        if (isPlatformBrowser(this.platformId)) {
            const jour1 = localStorage.getItem("seanceJour");
            const jour2: string | null = localStorage.getItem("jour");


            console.log(jour1);
            console.log(jour2);

            if (!jour2) {
                this.router.navigate(['']);
            }

            if (!jour1) {
                localStorage.setItem("seanceJour", jour2!);
            } else if (jour1 === jour2) {
                this.router.navigate(['recap-seance']);
            }


        }
    }




}
