import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { poidUpdate } from '../../poidUpdate'
import { Notification } from '../notification';


@Component({
    selector: 'app-menu-poid',
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './menu-poid.html',
    styleUrl: './menu-poid.css',
})
export class MenuPoid {

    poid = '';
    pDate = '';
    backendResponse = '';
    note: string | null = null;

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ser: poidUpdate, private not: Notification) { }

    ajouterPoid() {

        if (!this.note || this.note.trim() === '') {
            this.note = null;
        }

        this.http.post('http://127.0.0.1:5000/user/ajouterOuModifierPoids', {
            date: this.pDate,
            poids: this.poid,
            note: this.note
        }).subscribe({
            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.ser.triggerRefresh();
                this.cdr.detectChanges();

            },
            error: (err: any) => {
                //erreur 422
                if (err.error.code == 422 && err.error?.errors) {

                    const errorsObj = err.error.errors;
                    const messages: string[] = [];

                    for (const key in errorsObj) {

                        const value = errorsObj[key];
                        Object.values(value).forEach(v => {
                            if (Array.isArray(v)) messages.push(...v);
                            else if (typeof v === 'string') messages.push(v);
                            messages.push("\n");
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

    resetNotif() {
        this.not.reset(this, this.cdr);
    }

    supprimer() {
        if (!this.pDate || this.pDate.trim() === '') {
            this.backendResponse = "Veuillez rentrer une date";
            this.cdr.detectChanges();
            return;
        }
        const confirmAction = confirm("Voulez-vous vraiment supprimer votre enregistrement du " + this.pDate + "?");

        if (confirmAction) {

            this.http.delete('http://127.0.0.1:5000/user/suprimerPoid', {
                body: {
                    date: this.pDate
                }
            })
                .subscribe({

                    next: (res: any) => {
                        console.log('RESPONSE OK', res);
                        this.backendResponse = res.message;
                        this.cdr.detectChanges();

                    },

                    error: (err: any) => {
                        // erreurs HTTP (400, 409, 500…)
                        if (err.error && err.error.message) {
                            this.backendResponse = err.error.message; // <- message du backend
                        } else {
                            this.backendResponse = 'Erreur serveur';
                        }

                        this.cdr.detectChanges();
                    }
                });
        }

    }


}


