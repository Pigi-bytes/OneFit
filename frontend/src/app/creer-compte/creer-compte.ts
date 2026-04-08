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
    selector: 'app-creer-compte',
    standalone: true,
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './creer-compte.html',
    styleUrl: './creer-compte.css',
})
export class CreerCompte {

    username = '';
    password = '';
    backendResponse = '';
    confirmPassword = '';
    acceptedCompliance = false;
    isDark = false;

    constructor(private http: HttpClient, private router: Router, private erreur: Erreur,
        private cdr: ChangeDetectorRef, private not: Notification, private theme: Theme) { }

    /**
     * Crée un nouveau compte utilisateur
     * Vérifie la conformité et la correspondance des mots de passe
     * Effectue l'inscription puis la connexion automatique
     */
    creer() {
        if (!this.acceptedCompliance) {
            this.backendResponse = 'Vous devez accepter la politique de conformité avant de créer un compte.';
            return;
        }

        if (this.password !== this.confirmPassword.trim()) {
            this.backendResponse = 'Les mots de passe ne correspondent pas.';
            return;
        }

        this.http.post('http://127.0.0.1:5000/auth/inscription', {
            username: this.username,
            password: this.password

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.cdr.detectChanges();

                // connexion auto après l'inscription
                this.http.post('http://127.0.0.1:5000/auth/login', {
                    username: this.username,
                    password: this.password
                }).subscribe((res: any) => {
                    localStorage.setItem('access_token', res.access_token);
                    this.router.navigate(['/configurer-compte']);
                });
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
     * Initialise le composant, vérifie le thème sombre
     */
    ngOnInit() {
        this.isDark = this.theme.isItDark();
    }

}
