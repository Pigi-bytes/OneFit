import { Component } from '@angular/core';
import { AfficherExo } from '../afficher-exo/afficher-exo';
import { AjouterExo } from '../ajouter-exo/ajouter-exo';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt'
import { ChangeDetectorRef } from '@angular/core';
import { ConfigurerExo } from '../configurer-exo/configurer-exo';
import { Message } from '../../message';

@Component({
    selector: 'app-exercices',
    imports: [AjouterExo, AfficherExo, CommonModule, ConfigurerExo],
    templateUrl: './exercices.html',
    styleUrl: './exercices.css',
})
export class Exercices {

    exo: any;
    afficherComposant: "afficher" | "configue" = "afficher"; // composant par défaut
    exoId: any = null; // ID à passer si besoin
    private subscription?: Subscription;
    composantKey = 0;

    constructor(private etl: EnvoyerElt, private cdr: ChangeDetectorRef) { }

    /**
     * Initialise le composant : configure l'abonnement pour afficher/configurer les exercices
     */
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
                this.etl.triggerRefresh([Message.SELECTION_EXERCICE, this.exoId]);
            }
            this.composantKey++;
            this.cdr.detectChanges();
        });

    }

}

