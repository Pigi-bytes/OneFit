import { Component, inject, PLATFORM_ID } from '@angular/core';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { isPlatformBrowser } from '@angular/common';


@Component({
    selector: 'app-configurer-exo',
    imports: [FormsModule, CommonModule],
    templateUrl: './configurer-exo.html',
    styleUrl: './configurer-exo.css',
})
export class ConfigurerExo {

    private subscription?: Subscription;
    idExo = "";
    backendResponse = "";
    exo: any;
    setNumber = null;
    repNumber = null;
    poids = null;
    jour: any | null = null;
    private platformId = inject(PLATFORM_ID);


    constructor(private ei: EnvoyerElt, private http: HttpClient, private cdr: ChangeDetectorRef, private not: Notification) { }

    ngOnInit() {
        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");

        }
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            this.idExo = id[1];
            this.chargeExo();
        });
    }

    chargeExo() {
        this.http.post('http://127.0.0.1:5000/externe/getExo', {
            exoId: this.idExo,

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exo = res;
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

    ajouter() {
        this.http.post('http://127.0.0.1:5000/sport/ajouterExoSeance', {
            routine_id: -1,
            day: this.jour,
            exercise_id: this.idExo,
            planned_sets: this.setNumber,
            planned_reps: this.repNumber,
            planned_weight: this.poids


        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exo = res;
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

        this.ei.triggerRefresh([1, null, "ajouté avec sucée"]);
    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }

    annuler() {
        this.ei.triggerRefresh([1, null]);
    }

}
