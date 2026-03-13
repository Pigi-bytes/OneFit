import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AfficheSceance } from '../afficher-seance/afficher-seance';
import { ConfigurerExo } from '../configurer-exo/configurer-exo';
import { EnvoyerElt } from '../envoyerElt';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-seance',
    imports: [AfficheSceance, ConfigurerExo, CommonModule],
    templateUrl: './seance.html',
    styleUrl: './seance.css',
})
export class Seance {

    exo: any;
    afficherComposant: "afficher" | "configue" = "afficher"; // composant par défaut
    exoId: any = null; // ID à passer si besoin
    private subscription?: Subscription;
    composantKey = 0;

    constructor(private etl: EnvoyerElt, private cdr: ChangeDetectorRef) { }

    ngOnInit() {

        this.subscription = this.etl.afficheExercice$.subscribe((payload) => {
            if (Array.isArray(payload) && payload[0] != 2) {
                const type = payload[0];
                const id = payload[1];

                this.exoId = id;

                if (type === 0) {
                    this.afficherComposant = 'configue';        // redirige vers TestComposant
                } else if (type === 1) {
                    this.afficherComposant = 'afficher';    // redirige vers AfficherExo
                }

                this.cdr.detectChanges();
                this.etl.triggerRefresh([2, this.exoId]);
            }
            this.composantKey++;
            this.cdr.detectChanges();
        });

    }

}
