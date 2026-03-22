import { Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';
import { EnvoyerElt } from '../envoyerElt';
import { Chrono } from '../chrono/chrono';

@Component({
    selector: 'app-exercice-en-cours',
    imports: [Chrono, FormsModule, CommonModule, RouterModule],
    templateUrl: './exercice-en-cours.html',
    styleUrl: './exercice-en-cours.css',
})
export class ExerciceEnCours {

    jour: string | null = "";
    private platformId = inject(PLATFORM_ID);
    private subscription?: Subscription;
    exo: any;
    backendResponse = "";
    seance_exercise_id: any = 1;

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private router: Router,
        private ei: EnvoyerElt,
    ) { }

    ngOnInit() {
        if (isPlatformBrowser(this.platformId) && localStorage.getItem("lastMessage")) {
            this.seance_exercise_id = Number(localStorage.getItem("lastSequence"));;
        }
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            if (id[0] === Message.ENVOYER_ID_EXO) {
                this.seance_exercise_id = id[1];
                localStorage.setItem("lastSequence", this.seance_exercise_id.toString());
                localStorage.setItem("lastMessage", Message.ENVOYER_ID_EXO.toString());
            }
        });
        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            this.chargerExo();
        }

        this.cdr.detectChanges();
    }

    chargerExo() {
        this.http.post('http://127.0.0.1:5000/seance/getSeanceDuJour', {
            routine_id: -1,
            day: this.jour

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exo = res.seance.exercises.find((e: { seance_exercise_id: any; }) => e.seance_exercise_id === this.seance_exercise_id) ?? null;
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

    ajouterSet() {
        if (this.exo.planned_sets < 30) {
            this.exo.planned_sets += 1;
            this.cdr.detectChanges();
        }
    }

    supprimerSet() {
        if (this.exo.planned_sets > 1) {
            this.exo.planned_sets -= 1;
            this.cdr.detectChanges();
        }
    }


    range(n: number) {
        return Array.from({ length: n }, (_, i) => i + 1);
    }
}
