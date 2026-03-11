import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt'
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-choisir-routine',
    imports: [CommonModule, RouterModule],
    templateUrl: './choisir-routine.html',
    styleUrl: './choisir-routine.css',
})

export class ChoisirRoutine {
    backendResponse = "";
    routines: any[] = [];
    private routineActivatedSubscription?: Subscription;

    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }

    ngOnInit() {
        this.getRoutines();
        this.routineActivatedSubscription = this.ei.routineActivated$.subscribe(() => {
            this.getRoutines();
        });
    }
    
    getRoutines() {
        this.http.get('http://127.0.0.1:5000/sport/getRoutines', {}).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.routines = res.routines.map((r: any) => ({
                    nom: r["name"],
                    id: r["id"],
                    isActive: r["is_active"],
                }));

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

    AfficherInfosRoutine(id: any) {
        console.log(id);
        this.ei.triggerRefresh(id);
    }
}
