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
import { Erreur } from '../erreur';
import { AideExo } from '../aide-exo/aide-exo';

@Component({
    selector: 'app-exercice-en-cours',
    imports: [Chrono, FormsModule, CommonModule, RouterModule, AideExo],
    templateUrl: './exercice-en-cours.html',
    styleUrl: './exercice-en-cours.css',
})
export class ExerciceEnCours {

    jour: string | null = "";
    private platformId = inject(PLATFORM_ID);
    private subscription?: Subscription;
    exo: any;
    exoInfo: any;
    backendResponse = "";
    seance_exercise_id: any = 1;
    setsValides: { reps: any, weight: any }[] = [];
    isModalOpen = false;
    private exo2: any = null;

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private router: Router,
        private ei: EnvoyerElt,
        private erreur: Erreur
    ) { }

    ngOnInit() {

        if (isPlatformBrowser(this.platformId)) {
            const exo1 = localStorage.getItem("exoCourrant");
            this.exo2 = localStorage.getItem("exoVisualise");


            if (!this.exo2) {
                this.router.navigate(['']);
            }

            if (exo1 && this.exo2) {
                if (exo1 === this.exo2) {
                    this.router.navigate(['seance-en-cours']);
                } else {
                    localStorage.setItem("exoCourrant", this.exo2);
                }
            }

        }


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

                // remplir setsvalides avec sets vides
                if (this.exo) {
                    this.setsValides = Array.from({ length: this.exo.planned_sets }, () => ({ reps: null, weight: null }));
                }

                this.chargerInfoExo();
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }

    chargerInfoExo() {
        if (this.exo.exoId !== null) {
            this.http.post('http://127.0.0.1:5000/externe/getExo', {
                exoId: this.exo.exoId
            }).subscribe({
                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.exoInfo = res;
                },
                error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
            });
        }
    }

    ajouterSet() {
        if (this.exo.planned_sets < 30) {
            this.exo.planned_sets += 1;
            this.setsValides.push({ reps: null, weight: null });
            this.cdr.detectChanges();
        }
    }

    supprimerSet() {
        if (this.exo.planned_sets > 1) {
            this.exo.planned_sets -= 1;
            this.setsValides.pop();
            this.cdr.detectChanges();
        }
    }

    validerExo() {
        this.http.post('http://127.0.0.1:5000/seanceReelle/ajouterExoEffectue', {
            seance_exercise_id: this.exo.seance_exercise_id,
            sets: this.setsValides
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.ei.unblockExercice();
                this.ei.addExercice(this.seance_exercise_id);
                if (isPlatformBrowser(this.platformId)) {
                    localStorage.setItem("exoCourrant", this.exo2!);

                }

                this.ei.soumettre();

                this.ei.triggerRefresh([Message.SEANCE_EN_COURS]);
                localStorage.removeItem("coteExo");

                this.router.navigate(['/seance-en-cours']);
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });


    }

    openModal(id: any) {
        this.isModalOpen = true;
    }

    range(n: number) {
        return Array.from({ length: n }, (_, i) => i + 1);
    }
}
