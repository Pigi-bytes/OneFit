import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt';
import { Subscription } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';

@Component({
    selector: 'app-afficher-exo',
    standalone: true,
    imports: [RouterModule, CommonModule],
    templateUrl: './afficher-exo.html',
    styleUrl: './afficher-exo.css',
})
export class AfficherExo {
    private platformId = inject(PLATFORM_ID);
    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }
    backendResponse = "";
    id = null;
    exo: any;
    message: any | null = null;
    private subscription?: Subscription;

    ngOnInit() {
        this.exo = null;
        this.message = null;
        if (isPlatformBrowser(this.platformId)) {
            this.message = localStorage.getItem("message");
            this.cdr.detectChanges();
            localStorage.removeItem("message");
        }
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            if (id[0] !== 1) return;

            if (this.id === id[1]) return

            if (id[0] === Message.AFFICHER_SEANCE) {
                this.message = null;
                this.modifId(id[1]);
                this.chargeExo();
            }


        });
    }

    modifId(id: any) {
        this.id = id;
    }

    chargeExo() {
        if (this.id !== null) {
            this.http.post('http://127.0.0.1:5000/externe/getExo', {
                exoId: this.id,

            }).subscribe({

                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.exo = res;
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

    ngOnDestroy() {
        this.subscription?.unsubscribe();
    }
}
