import { Component } from '@angular/core';
import { Subscription } from 'rxjs';
import { EnvoyerElt } from '../envoyerElt';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


@Component({
    selector: 'app-configurer-exo',
    imports: [FormsModule, CommonModule],
    templateUrl: './configurer-exo.html',
    styleUrl: './configurer-exo.css',
})
export class ConfigurerExo {

    private subscription?: Subscription;
    id = "";
    backendResponse = "";
    exo: any;
    setNumber = null;
    repNumber = null;
    poids = null;


    constructor(private ei: EnvoyerElt, private http: HttpClient, private cdr: ChangeDetectorRef, private not: Notification) { }

    ngOnInit() {
        this.subscription = this.ei.afficheExercice$.subscribe((id) => {
            this.id = id[1];
            console.log(this.id);
            this.chargeExo();
        });
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

    ajouter() {

    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }

    annuler() {
        this.ei.triggerRefresh([1, null]);
    }

}
