import { Component, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { ChangeDetectorRef } from '@angular/core';
import { Chrono } from '../chrono/chrono';
import { Message } from '../../message';
import { EnvoyerElt } from '../envoyerElt';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-recap-seance',
    imports: [Chrono, RouterModule, CommonModule],
    templateUrl: './recap-seance.html',
    styleUrl: './recap-seance.css',
})
export class RecapSeance {
    name: any
    private platformId = inject(PLATFORM_ID);
    exercices: any[] = [];
    recapExo: any[] = [];
    backendResponse = "";
    jour: string | null = null;
    streak: any = null;

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ei: EnvoyerElt, private route: Router, private erreur: Erreur) { }


    ngOnInit() {

        if (isPlatformBrowser(this.platformId) && localStorage.getItem("noRecap")) {
            this.route.navigate(['accueil']);
        }
        this.ei.triggerRefresh([Message.CHRONO_RECAP]);
        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.route.navigate(['']);
                alert("Veuillez-vous connecter.")
                return;
            }
            this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
                this.name = res.username;
            });
        }

        this.chargeSeance();
        this.recupStrick();

        this.cdr.detectChanges();
    }

    terminer() {
        this.ei.triggerRefresh([Message.FINIR_RECAP]);
        this.route.navigate(['/accueil']);

    }

    chargeSeance() {
        this.http.post('http://127.0.0.1:5000/seance/getSeanceDuJour', {
            routine_id: -1,
            day: this.jour

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exercices = res.seance.exercises.sort((a: any, b: any) => a.ordre - b.ordre);

                this.backendResponse = res.message;

            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }

    recupStrick() {
        this.http.get('http://127.0.0.1:5000/user/getStreak', {}).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.streak = res['current_streak'];
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }


}
