import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt'
import { TooltipMoveDirective } from '../tooltipmove';
import { Message } from '../../message';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-ajouter-exo',
    standalone: true,
    imports: [FormsModule, CommonModule, RouterModule, TooltipMoveDirective],
    templateUrl: './ajouter-exo.html',
    styleUrl: './ajouter-exo.css',
})
export class AjouterExo {
    backendResponse = "";
    nom = "";
    exercices: any[] = [];


    constructor(private http: HttpClient, private erreur: Erreur, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }

    trouverExo() {
        this.http.post('http://127.0.0.1:5000/externe/searchExo', {
            recherche: this.nom,

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);

                this.exercices = res.resultats.map((exo: any) => ({
                    nom: exo[0],
                    id: exo[1],
                    image: exo[2]
                }));

                this.cdr.detectChanges();

            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }



    resetNotif() {
        this.not.reset(this, this.cdr);
    }


    ajouterExo(id: any) {
        this.ei.triggerRefresh([Message.AFFICHER_CONFIGURATEUR, id]);
    }

    AfficherInfosExo(id: any) {
        this.ei.triggerRefresh([Message.AFFICHER_SEANCE, id]);
    }

}