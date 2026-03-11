import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-afficher-routine',
    standalone: true,
    imports: [RouterModule, CommonModule],
    templateUrl: './afficher-routine.html',
    styleUrl: './afficher-routine.css',
})
export class AfficherRoutine {
    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }
    backendResponse = "";
    id = null;
    seances: any;
    private subscription?: Subscription;

    ngOnInit() {
        this.seances = null;
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            this.modifId(id);
            this.chargeRoutine();
        });
        this.chargeRoutine();
    }

    modifId(id: any) {
        this.id = id.toString();
    }

    chargeRoutine() {
        this.http.post('http://127.0.0.1:5000/sport/getSeancesPrevu', {
            routine_id: this.id,
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.seances = res.seances;
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
