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

    coteExo: boolean = false;
    coteRecap: boolean = false;

    private intervalId: any;

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
            if (id[0] === Message.RESET_CHRONO) {
                this.isRunning = false;
                this.commencerEnrgScenace();
                this.finirEnrgSceance();
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
                this.finirEnrgSceance();


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
    ngAfterViewInit() {
        if (isPlatformBrowser(this.platformId) && this.isRunning) {
            this.startChrono();
        }
    }

    ngOnDestroy() {
        this.stopChrono();
    }

    private startChrono() {
        if (!isPlatformBrowser(this.platformId)) return;
        if (!this.intervalId) {
            this.intervalId = setInterval(() => this.tick(), 1000);
        }
    }

    private stopChrono() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    private tick() {
        this.seconde++;
        if (this.seconde >= 60) { this.seconde = 0; this.minute++; }
        if (this.minute >= 60) { this.minute = 0; this.heure++; }

        this.updateTemps();

        if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem("chronoTemps", this.temps);
        }
    }

    private updateTemps() {
        this.temps = [this.heure, this.minute, this.seconde]
            .map(v => String(v).padStart(2, '0'))
            .join(':');
    }

    private resetChrono() {
        localStorage.removeItem("chronoTemps");
    }

    retour() {
        if (this.coteExo) {
            this.elt.triggerRefresh([Message.SEANCE_EN_COURS]);
            localStorage.removeItem("lastSequence");
            localStorage.removeItem("coteExo");
            this.router.navigate(['/seance-en-cours']);
        } else {
            if (confirm("voulez vous quitter la séance en cours (elle ne serat pas enregistrée)")) {
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
                this.router.navigate(['/accueil']);

            }
        }
    }


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

    finirEnrgSceance() {
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

    }
}