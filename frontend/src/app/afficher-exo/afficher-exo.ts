import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnvoyerId } from '../envoyer-id';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-afficher-exo',
    standalone: true,
    imports: [RouterModule, CommonModule],
    templateUrl: './afficher-exo.html',
    styleUrl: './afficher-exo.css',
})
export class AfficherExo {
    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerId) { }
    backendResponse = "";
    id = null;
    exo: any;
    private subscription?: Subscription;

    ngOnInit() {
        this.exo = null;
        this.subscription = this.ei.afficheExcercice$.subscribe((id) => {
            this.modifId(id);
            this.chargeExo();
        });
        this.chargeExo();
    }

    modifId(id: any) {
        this.id = id;
        console.log("coucou");
    }

    chargeExo() {
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
