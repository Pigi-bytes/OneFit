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

@Component({
    selector: 'app-recap-sceance',
    imports: [Chrono, RouterModule, CommonModule],
    templateUrl: './recap-sceance.html',
    styleUrl: './recap-sceance.css',
})
export class RecapSceance {
    name: any
    private platformId = inject(PLATFORM_ID);
    exercices: any[] = [];
    recapExo: any[] = [];
    backendResponse = "";
    jour: string | null = null;

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ei: EnvoyerElt, private route: Router) { }


    ngOnInit() {
        this.ei.triggerRefresh([Message.CHRONO_RECAP]);
        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.route.navigate(['']);
                alert("veuillez vous connecter")
                return;
            }
            this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
                this.name = res.username;
            });
        }

        this.chargeSeance();

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
                if (this.exercices.length === 0) {
                    this.ei.triggerRefresh([Message.RESET_CHRONO]);
                    this.cdr.detectChanges();
                }
                this.backendResponse = res.message;

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
