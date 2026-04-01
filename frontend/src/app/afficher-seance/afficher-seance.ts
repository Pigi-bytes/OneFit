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
import { distinctUntilChanged } from 'rxjs/operators';
import { Erreur } from '../erreur';

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
    exercicesValide: any[] = [];
    backendResponse = "";
    commencerSeance: boolean = false;
    seanceRepos: boolean = false;
    private subscriptions: Subscription[] = [];

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private net: Notification,
        private ei: EnvoyerElt,
        private router: Router,
        private erreur: Erreur
    ) { }

    ngOnInit() {

        if (isPlatformBrowser(this.platformId) && localStorage.getItem("lastMessage")) {

            if (localStorage.getItem("lastMessage") === Message.SEANCE_EN_COURS.toString()) {
                this.commencerSeance = true;

            }
        }


        this.subscriptions.push(
            this.ei.commencerSceance$.subscribe(() => {
                this.commencerSeance = true;
                localStorage.setItem("lastMessage", Message.SEANCE_EN_COURS.toString());
            })
        );

        this.subscriptions.push(
            this.ei.afficheExercice$.subscribe((msg) => {
                if (msg[0] === Message.AFFICHER_SEANCE) {
                    this.chargeSeance();
                }
            })
        );

        this.subscriptions.push(
            this.ei.exercices$.subscribe(data => {
                this.exercicesValide = data;
                console.log('Exercices reçus:', this.exercicesValide);
                this.ei.blockExercice();
            })
        );

        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            this.chargeSeance();
        }

        this.cdr.detectChanges();

    }

    chargeSeance() {
        this.http.post('http://127.0.0.1:5000/seance/getSeanceDuJour', {
            routine_id: -1,
            day: this.jour

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exercices = res.seance.exercises.sort((a: any, b: any) => a.ordre - b.ordre);

                for (const exo of this.exercices) {
                    if (this.exercicesValide.some(e => e === exo.seance_exercise_id)) {
                        exo['dejaValide'] = true;
                    }
                }
                if (this.exercices.length === 0 && this.commencerSeance) {

                    this.seanceRepos = true;
                    this.ei.triggerRefresh([Message.ENR_REPOS]);
                    this.cdr.detectChanges();
                }
                this.backendResponse = res.message;

            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
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
            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
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
            if (isPlatformBrowser(this.platformId)) {
                localStorage.setItem("exoVisualise", idSequence!);

            }

            this.ei.triggerRefresh([Message.CHRONO_EXO]);
            this.ei.triggerRefresh([Message.ENVOYER_ID_EXO, idSequence]);
            this.router.navigate(['/exercice-en-cours']);
        }

    }

    retour() {

        if (this.commencerSeance && !this.seanceRepos) {
            for (const exo of this.exercices) {
                if (!this.exercicesValide.some(e => e === exo.seance_exercise_id)) {
                    alert("il faut valider tout les exercies pour terminer la scéance");
                    return;
                }

            }

            this.ei.blockSeance();
            this.ei.resetExercice();
            if (isPlatformBrowser(this.platformId)) {
                localStorage.setItem("seanceJour", localStorage.getItem("jour")!);
            }

            this.ei.triggerRefresh([Message.FINIR_SEANCE]);
            localStorage.removeItem("lastMessage");
            this.router.navigate(['/recap-seance']);
        } else if (this.seanceRepos) {
            localStorage.removeItem("lastMessage");
            this.ei.blockSeance();
            this.router.navigate(['/accueil']);
        } else {
            localStorage.removeItem("lastMessage");
            this.router.navigate(['/routine']);
        }

    }

    ngOnDestroy() {
        this.subscriptions.map((sub) => sub.unsubscribe());

    }
}