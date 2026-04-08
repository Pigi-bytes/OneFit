import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';
import { Erreur } from '../erreur';
import { Theme } from '../theme';

@Component({
    selector: 'app-connexion',
    standalone: true,
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './connexion.html',
    styleUrl: './connexion.css'
})

export class Connexion {
    username = '';
    password = '';
    backendResponse = '';
    isDark = false;

    constructor(private http: HttpClient, private router: Router, private erreur: Erreur, private cdr: ChangeDetectorRef,
        private not: Notification, private theme: Theme) { }

    /**
     * Effectue la connexion de l'utilisateur
     * Envoie les identifiants au backend et stocke le token si réussi
     */
    login() {
        this.http.post('http://127.0.0.1:5000/auth/login', {
            username: this.username,
            password: this.password
        }).subscribe({
            next: (res: any) => {
                if (res.access_token) {
                    localStorage.setItem('access_token', res.access_token);
                    this.router.navigate(['/accueil']);
                } else {
                    this.backendResponse = 'Erreur de connexion';
                }
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    /**
     * Réinitialise les notifications
     */
    resetNotif() {
        this.not.reset(this, this.cdr);
    }

    /**
     * Initialise le composant : vérifie le thème sombre
     */
    ngOnInit() {
        this.isDark = this.theme.isItDark();
    }
}
