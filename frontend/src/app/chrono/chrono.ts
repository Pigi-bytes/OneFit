import { Component, OnInit, OnDestroy, Input, PLATFORM_ID, inject, AfterViewInit } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt';
import { RouterModule, Router } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Erreur } from '../erreur';
import { TooltipMoveDirective } from '../tooltipmove';


@Component({
    selector: 'app-chrono',
    imports: [RouterModule, CommonModule, TooltipMoveDirective],
    templateUrl: './chrono.html',
    styleUrl: './chrono.css',
})
export class Chrono implements OnInit, AfterViewInit, OnDestroy {

    @Input() isRunning: boolean = true;
    private platformId = inject(PLATFORM_ID);
    private subscription?: Subscription;

    constructor(private elt: EnvoyerElt, private router: Router, private cdr: ChangeDetectorRef, private http: HttpClient, private er: Erreur) { }

    heure = 0;
    minute = 0;
    seconde = 0;
    temps: string = "00:00:00";
    backendResponse = "";
    seances: any;

    coteExo: boolean = false;
    coteRecap: boolean = false;

    private intervalId: any;

    /**
     * Initialise le chronomètre : restaure l'état sauvegardé et configure les abonnements
     */
    ngOnInit() {
        this.coteExo = false;
        this.coteRecap = false;
        if (isPlatformBrowser(this.platformId)) {
            const savedRecap = localStorage.getItem("coteRecap");
            if (savedRecap === "true") {
                this.coteRecap = true;
                localStorage.setItem("coteRecap", "true");
            }
            const savedCoteExo = localStorage.getItem("coteExo");
            if (savedCoteExo === "true") {
                this.coteExo = true;
                localStorage.setItem("coteExo", "true");
            }
            const savedTime = localStorage.getItem("chronoTemps");
            if (savedTime) {
                [this.heure, this.minute, this.seconde] = savedTime.split(':').map(Number);
                this.updateTemps();
            }
        }

        this.subscription = this.elt.afficheExercice$.subscribe((id) => {
            if (id[0] === Message.ENR_REPOS) {
                this.isRunning = false;
                this.stopChrono();
                this.resetChrono();
            } else if (id[0] === Message.CHRONO_EXO) {
                this.coteExo = true;
                if (isPlatformBrowser(this.platformId)) {
                    localStorage.setItem("coteExo", "true");
                }
                this.cdr.detectChanges();
            } else if (id[0] === Message.COMMENCER_SEANCE && !localStorage.getItem("seanceEnCours")) {
                if (isPlatformBrowser(this.platformId)) {
                    localStorage.setItem("seanceEnCours", "enCours");
                }

                this.commencerEnrgScenace();



            } else if (id[0] === Message.FINIR_SEANCE && !localStorage.getItem("seanceFini")) {
                if (isPlatformBrowser(this.platformId)) {
                    localStorage.setItem("seanceFini", "fini");
                }
                this.finirEnrgSeance();


                this.isRunning = false;
                this.stopChrono();
                localStorage.removeItem("seanceEnCours");
                this.router.navigate(['/accueil']);
            } else if (id[0] === Message.CHRONO_RECAP) {
                this.coteRecap = true;
                this.isRunning = false;
                if (isPlatformBrowser(this.platformId)) {
                    localStorage.setItem("coteRecap", "true");
                }

            } else if (id[0] === Message.FINIR_RECAP) {
                this.resetChrono();
                localStorage.removeItem("coteRecap");
            }

        });
    }

    /**
     * Démarre le chronomètre après l'initialisation de la vue
     */
    ngAfterViewInit() {
        if (isPlatformBrowser(this.platformId) && this.isRunning) {
            this.startChrono();
        }
    }

    /**
     * Nettoie les ressources lors de la destruction du composant
     */
    ngOnDestroy() {
        this.stopChrono();
    }

    /**
     * Démarre le chronomètre
     */
    private startChrono() {
        if (!isPlatformBrowser(this.platformId)) return;
        if (!this.intervalId) {
            this.intervalId = setInterval(() => this.tick(), 1000);
        }
    }

    /**
     * Arrête le chronomètre
     */
    private stopChrono() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Met à jour le temps chaque seconde
     */
    private tick() {
        this.seconde++;
        if (this.seconde >= 60) { this.seconde = 0; this.minute++; }
        if (this.minute >= 60) { this.minute = 0; this.heure++; }

        this.updateTemps();

        if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem("chronoTemps", this.temps);
        }
    }

    /**
     * Met à jour la chaîne de temps formatée
     */
    private updateTemps() {
        this.temps = [this.heure, this.minute, this.seconde]
            .map(v => String(v).padStart(2, '0'))
            .join(':');
    }

    /**
     * Réinitialise le chronomètre
     */
    private resetChrono() {
        localStorage.removeItem("chronoTemps");
    }

    /**
     * Gère le retour : revient à la séance ou abandonne
     */
    retour() {
        if (this.coteExo) {
            this.elt.triggerRefresh([Message.SEANCE_EN_COURS]);
            localStorage.removeItem("lastSequence");
            localStorage.removeItem("coteExo");
            this.router.navigate(['/seance-en-cours']);
        } else {
            if (confirm("Voulez-vous quitter la séance en cours? Elle ne sera pas enregistrée.")) {
                this.resetChrono();
                localStorage.removeItem("lastMessage");
                this.http.delete('http://127.0.0.1:5000/seanceReelle/abandonSeanceReelle', {
                }).subscribe({
                    next: (res: any) => {
                        console.log('RESPONSE OK', res);
                        this.backendResponse = res.message;;
                    },

                    error: (err: any) => { this.backendResponse = this.er.erreur(err); this.cdr.detectChanges(); }

                });
                this.elt.blockSeance();
                this.elt.resetExercice();
                localStorage.removeItem("seanceJour");
                this.router.navigate(['/accueil']);

            }
        }
    }

    /**
     * Commence l'enregistrement de la séance
     */
    commencerEnrgScenace() {
        this.http.post('http://127.0.0.1:5000/seanceReelle/startSeanceEffectuee', {
            routine_id: -1,
            day: localStorage.getItem("jour"),

        }).subscribe({
            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;;
            },

            error: (err: any) => { this.backendResponse = this.er.erreur(err); this.cdr.detectChanges(); }

        });

    }

    /**
     * Termine l'enregistrement de la séance et enregistre les jours de repos
     */
    finirEnrgSeance() {

        this.http.post('http://127.0.0.1:5000/seance/getSeancesPrevu', {
            routine_id: -1,

        }).subscribe({
            next: (res: any) => {
                this.seances = res.seances;
                console.log('RESPONSE OK', res);

                const jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
                const jourActuel = localStorage.getItem("jour");
                const indexActuel = jours.indexOf(jourActuel!);

                let boucle = true;
                for (let i = 1; i < jours.length && boucle; i++) {
                    const index = (indexActuel - i + 7) % 7;
                    const jourCible = jours[index];

                    const seance = this.seances.find((s: any) => s.day === jourCible);

                    if (seance?.title === "Jour de Repos") {
                        const today = new Date();
                        today.setDate(today.getDate() - i);
                        const date = today.toISOString().split('T')[0];

                        this.enregRepos(jourCible, date);
                    } else {
                        boucle = false; // On arrête dès qu'on tombe sur une vraie séance
                    }
                }
                this.http.post('http://127.0.0.1:5000/seanceReelle/endSeanceEffectuee', {
                    routine_id: -1,
                    day: localStorage.getItem("jour"),

                }).subscribe({
                    next: (res: any) => {
                        console.log('RESPONSE OK', res);
                        this.backendResponse = res.message;;
                    },

                    error: (err: any) => { this.backendResponse = this.er.erreur(err); this.cdr.detectChanges(); }

                });

            },

            error: (err: any) => { this.backendResponse = this.er.erreur(err); this.cdr.detectChanges(); }

        });

    }


    /**
     * Enregistre une séance de repos pour un jour donné
     * @param day Jour de la semaine
     * @param date Date au format YYYY-MM-DD
     */
    enregRepos(day: any, date: any) {
        this.http.post('http://127.0.0.1:5000/seanceReelle/enregSeanceRepos', {
            routine_id: -1,
            day: day,
            date: date,

        }).subscribe({
            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;;
            },

            error: (err: any) => { this.backendResponse = this.er.erreur(err); this.cdr.detectChanges(); }

        });

    }
}