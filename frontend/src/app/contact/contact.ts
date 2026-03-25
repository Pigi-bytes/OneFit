import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { Erreur } from '../erreur';


@Component({
    selector: 'app-contact',
    imports: [FormsModule, CommonModule, RouterModule],
    templateUrl: './contact.html',
    styleUrl: './contact.css',
})
export class Contact {
    private platformId = inject(PLATFORM_ID);

    backendResponse = '';
    email = "";
    contenue = "";


    constructor(private cdr: ChangeDetectorRef, private not: Notification, private erreur: Erreur, private http: HttpClient) { }


    supprimer() {
        this.contenue = "";
        this.email = "";

    }

    resetNotif() {
        this.not.reset(this, this.cdr)
    }

    envoyerMail() {
        if (this.contenue != "" && this.email != "") {
            this.http.post('http://127.0.0.1:5000/user/envoyer_mail', {
                email: this.email,
                contenue: this.contenue


            }).subscribe({

                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.backendResponse = res.message;
                    this.cdr.detectChanges();
                    this.supprimer();
                },

                error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
            });

        } else {
            this.backendResponse = "Veuillez renseigner les champ";
            this.cdr.detectChanges();
        }



    }
}
