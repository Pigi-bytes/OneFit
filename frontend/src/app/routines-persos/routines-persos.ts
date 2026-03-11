import { Component } from '@angular/core';
import { ChoisirRoutine } from '../choisir-routine/choisir-routine';
import { AfficherRoutine } from '../afficher-routine/afficher-routine';

@Component({
  selector: 'app-routines-persos',
  imports: [AfficherRoutine, ChoisirRoutine],
  templateUrl: './routines-persos.html',
  styleUrl: './routines-persos.css',
})
export class RoutinesPersos {

}
