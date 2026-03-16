import { Component } from '@angular/core';
import { AfficheSceance } from '../afficher-seance/afficher-seance';
import { Chrono } from '../chrono/chrono';

@Component({
    selector: 'app-seance-en-cours',
    imports: [Chrono, AfficheSceance],
    templateUrl: './seance-en-cours.html',
    styleUrl: './seance-en-cours.css',
})
export class SeanceEnCours {

}
