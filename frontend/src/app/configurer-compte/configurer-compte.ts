import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-configurer-compte',
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './configurer-compte.html',
    styleUrl: './configurer-compte.css',
})
export class ConfigurerCompte {

    height = '';
    birthDate = '';
    backendResponse = '';

    constructor(private http: HttpClient, private router: Router, private erreur: Erreur, private cdr: ChangeDetectorRef, private not: Notification) { }

    configurer() {
        this.http.post('http://127.0.0.1:5000/user/option/configurer', {
            taille: this.height,
            date_naissance: this.birthDate
        }).subscribe({
            next: (res: any) => {
                this.backendResponse = res.message;
                this.cdr.detectChanges();
                this.router.navigate(['/accueil']);
            },
            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }
}
