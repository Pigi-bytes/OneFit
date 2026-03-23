import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { poidUpdate } from '../../poidUpdate'
import { Notification } from '../notification';
import { Erreur } from '../erreur';


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

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private erreur: Erreur, private ser: poidUpdate, private not: Notification) { }

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
            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
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
                        this.ser.triggerRefresh();

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


