import { Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EnvoyerElt } from '../envoyerElt';
import { Notification } from '../notification';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';
import { TooltipMoveDirective } from '../tooltipmove';

@Component({
    selector: 'app-afficher-seance',
    imports: [FormsModule, CommonModule, RouterModule, TooltipMoveDirective],
    templateUrl: './afficher-seance.html',
    styleUrls: ['./afficher-seance.css'],
})
export class AfficheSceance implements OnInit {

    private subscription?: Subscription;
    private platformId = inject(PLATFORM_ID);
    jour: string | null = "";
    exercices: any[] = [];
    backendResponse = "";
    commencerSeance: boolean = false;

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private net: Notification,
        private ei: EnvoyerElt,
        private router: Router,

    ) { }

    ngOnInit() {

        if (isPlatformBrowser(this.platformId) && localStorage.getItem("lastMessage")) {
            if (localStorage.getItem("lastMessage") === Message.SEANCE_EN_COURS.toString()) {
                this.commencerSeance = true;

            }
        }


        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            if (id[0] === Message.SEANCE_EN_COURS || id[0] === Message.COMMENCER_SEANCE) {
                this.commencerSeance = true;
                localStorage.setItem("lastMessage", Message.SEANCE_EN_COURS.toString());
            }
        });

        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            this.chargeSeance();
        }

        this.cdr.detectChanges();

        // récupère le paramètre 'id' de la route

    }

    chargeSeance() {
        this.http.post('http://127.0.0.1:5000/seance/getSeanceDuJour', {
            routine_id: -1,
            day: this.jour

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exercices = res.seance.exercises.sort((a: any, b: any) => a.ordre - b.ordre);;
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


    bouger(id: any, sens: string) {
        const index = this.exercices.findIndex(e => e.seance_exercise_id === id);

        if (index === -1) return;

        if (sens === 'up' && index > 0) {

            [this.exercices[index], this.exercices[index - 1]] =
                [this.exercices[index - 1], this.exercices[index]];

        }

        if (sens === 'down' && index < this.exercices.length - 1) {

            [this.exercices[index], this.exercices[index + 1]] =
                [this.exercices[index + 1], this.exercices[index]];

        }

        this.http.post('http://127.0.0.1:5000/seance/deplacerOrdreExoSeance', {
            routine_id: -1,
            day: this.jour,
            seance_exercise_id: id,
            direction: sens

        }).subscribe({
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

            }
        });

        this.cdr.detectChanges();

    }


    trackByExo(index: number, item: any) {
        return item.seance_exercise_id;
    }

    ajouterExo() {
        this.router.navigate(['/exercices']);
    }

    modifie(id: any, nbRep: any, nbSet: any, poid: any, idSequence: any) {
        if (!this.commencerSeance) {
            this.ei.triggerRefresh([Message.MODIFIER_EXERCICE, id, nbRep, nbSet, poid, idSequence]);
        } else {
            this.ei.triggerRefresh([Message.CHRONO_EXO]);
            this.ei.triggerRefresh([Message.ENVOYER_ID_EXO, idSequence]);
            this.router.navigate(['/exercice-en-cours']);
        }

    }

    retour() {
        if (this.commencerSeance) {
            this.ei.triggerRefresh([Message.FINIR_SEANCE]);
            localStorage.removeItem("lastMessage");
            this.router.navigate(['/recap-seance']);
        } else {
            localStorage.removeItem("lastMessage");
            this.router.navigate(['/routine']);
        }

    }

    ngOnDestroy() {
        this.subscription?.unsubscribe();
    }
}