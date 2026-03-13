import { Component, inject, PLATFORM_ID } from '@angular/core';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { isPlatformBrowser } from '@angular/common';
import { threadId } from 'worker_threads';


@Component({
    selector: 'app-configurer-exo',
    imports: [FormsModule, CommonModule],
    templateUrl: './configurer-exo.html',
    styleUrl: './configurer-exo.css',
})
export class ConfigurerExo {

    private subscription?: Subscription;
    idExo: any;
    backendResponse = "";
    exo: any;
    setNumber = null;
    repNumber = null;
    poids = null;
    jour: any | null = null;
    modifie: any | null = null;
    private platformId = inject(PLATFORM_ID);


    constructor(private ei: EnvoyerElt, private http: HttpClient, private cdr: ChangeDetectorRef, private not: Notification) { }

    ngOnInit() {
        this.exo = null;
        this.modifie = "";
        this.idExo = null;

        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");

        }
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            alert("test")
            console.log(id);
            if (id[0] === 3) {
                this.idExo = id[1];
                this.modifie = "";
                this.setNumber = id[2];
                this.repNumber = id[3];
                this.poids = id[4];
                this.cdr.detectChanges();
            }
            else if (id[0] === 0 || id[0] === 2) {
                this.idExo = id[1];
                this.modifie = null;
                this.chargeExo();
            }

        });
        console.log(this);
    }

    async chargeExo() {
        if (this.idExo) {
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
    }

    action() {
        if (!this.modifie) {
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

            localStorage.setItem("message", "ajouté avec sucée");
            this.ei.triggerRefresh([1, null]);
        }
    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }

    annuler() {
        this.ei.triggerRefresh([1, null]);
    }

    ngOnDestroy() {
        this.subscription?.unsubscribe();
    }

}
