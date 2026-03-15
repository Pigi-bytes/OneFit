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


    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }

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

            error: (err: any) => {
                //erreur 422
                if (err.status == 422 && err.error.errors) {

                    const errorsObj = err.error.errors;
                    const messages: string[] = [];



                    for (const key in errorsObj) {

                        const value = errorsObj[key];
                        Object.values(value).forEach(v => {
                            if (Array.isArray(v)) messages.push(...v);
                            else if (typeof v === 'string') messages.push(v);
                        });
                    }

                    this.backendResponse = messages.join('\n');
                }
                // erreurs HTTP (400, 409, 500…)
                else if (err.error && err.error.message) {
                    this.backendResponse = err.error.message; // <- message du backend
                } else {
                    this.backendResponse = 'Erreur serveur';
                }
                this.cdr.detectChanges();
            }
        });

    }



    resetNotif() {
        this.not.reset(this, this.cdr);
    }


    ajouterExo(id: any) {
        this.ei.triggerRefresh([Message.AFFICHER_CONFIGURATEUR, id]);
    }

    AfficherInfosExo(id: any) {
        this.ei.triggerRefresh([Message.AFFICHER_CONFIGURATEUR, id]);
    }



}