import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt'
import { Subscription } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-afficher-routine',
    standalone: true,
    imports: [RouterModule, CommonModule, FormsModule],
    templateUrl: './afficher-routine.html',
    styleUrl: './afficher-routine.css',
})
export class AfficherRoutine {
    constructor(private http: HttpClient,private erreur: Erreur, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }
    backendResponse = "";
    id = null;
    routine: any;
    routine_nom = "";
    seances: any;
    private subscription?: Subscription;
    is_renaming = false;

    ngOnInit() {
        this.seances = null;
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            this.modifId(id);
            this.chargerInfosRoutines();
            this.chargerSeances();
            this.is_renaming = false;
        });
    }

    modifId(id: any) {
        this.id = id.toString();
    }

    chargerInfosRoutines(){
        this.http.post('http://127.0.0.1:5000/routine/getRoutine', {
            routine_id: this.id,
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.routine = res;
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    chargerSeances() {
        this.http.post('http://127.0.0.1:5000/seance/getSeancesPrevu', {
            routine_id: this.id,
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.seances = res.seances;
                this.backendResponse = res.message;
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

    activerRoutine(){
        this.http.post('http://127.0.0.1:5000/routine/activerRoutine', {
            routine_id: this.id,
        }).subscribe({
            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.ei.triggerRefresh(null);
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

    supprimerRoutine(){
        const confirmAction = confirm("Voulez-vous vraiment supprimer cette routine ?");

        if (confirmAction){
            this.http.delete('http://127.0.0.1:5000/routine/supprimerRoutine', {
                body: {
                    routine_id: this.id
                }
            }).subscribe({
                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.backendResponse = res.message;
                    this.ei.triggerRefresh(null);
                    this.cdr.detectChanges();
                },

                error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
            });

        }
    }

    ouvrirFormulaireRenommerRoutine(){
        this.is_renaming = true;
        this.cdr.detectChanges();
    }

    renommerRoutine(){
        this.http.post('http://127.0.0.1:5000/routine/modiferNomRoutine', {
            routine_id: this.id,
            name: this.routine_nom
        }).subscribe({
            next: (res: any) => {
                this.routine.name = res.name ?? this.routine_nom;
                this.is_renaming = false;
                this.backendResponse = res.message;
                this.ei.triggerRefresh(null);
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
    

}