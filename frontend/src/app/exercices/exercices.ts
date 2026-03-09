import { Component } from '@angular/core';
import { AfficherExo } from '../afficher-exo/afficher-exo';
import { AjouterExo } from '../ajouter-exo/ajouter-exo';

@Component({
    selector: 'app-exercices',
    imports: [AjouterExo, AfficherExo],
    templateUrl: './exercices.html',
    styleUrl: './exercices.css',
})
export class Exercices {

}
