import { Component } from '@angular/core';
import { AfficheSceance } from '../affiche-sceance/affiche-sceance';
import { ModifeExercice } from '../modife-exercice/modife-exercice';

@Component({
    selector: 'app-seance',
    imports: [AfficheSceance, ModifeExercice],
    templateUrl: './seance.html',
    styleUrl: './seance.css',
})
export class Seance {

}
