import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AfficheSceance } from '../afficher-seance/afficher-seance';
import { ConfigurerExo } from '../configurer-exo/configurer-exo';
import { EnvoyerElt } from '../envoyerElt';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-seance',
    imports: [AfficheSceance, ConfigurerExo],
    templateUrl: './seance.html',
    styleUrl: './seance.css',
})
export class Seance {

    private subscription?: Subscription;

    constructor(private elt: EnvoyerElt) { }


    ngOnInit() {
        this.subscription = this.elt.afficheExercice$.subscribe((payload) => {
            if (payload[0] === 5) {
                this.elt.triggerRefresh([4]);

            }


        });

    }

}
