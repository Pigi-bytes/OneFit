import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Theme } from '../theme';
import { Notification } from '../notification';

@Component({
    selector: 'app-utilisateur',
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './utilisateur.html',
    styleUrl: './utilisateur.css',
})
export class Utilisateur {

    private http = inject(HttpClient);
    private platformId = inject(PLATFORM_ID);
    private router = inject(Router);

    username = '';
    backendResponse = '';
    taille = '';
    Busername = '';
    birthDate = '';

    private oldUsername = '';
    private oldDate = '';
    private oldTaille = '';

    constructor(private cdr: ChangeDetectorRef, private theme: Theme, private not: Notification) { }
    isDark = false;

    ngOnInit() {
        if (isPlatformBrowser(this.platformId)) {
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.router.navigate(['']);
                alert("veuillez vous connecter")
                return;
            }
            this.getAllinformation();
        }
    }


    toggleTheme() {
        this.theme.toggleDark();
        this.isDark = document.body.classList.contains('dark');

        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('darkMode', String(this.isDark));
        }
    }


    getAllinformation() {
        this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
            this.username = res.username;
            this.taille = res.taille;
            this.birthDate = res.date_naissance;

            this.oldUsername = this.username;
            this.oldDate = this.birthDate;
            this.oldTaille = this.taille
            console.log('User:', res);

        });

    }

    modif() {
        if ((this.oldTaille != this.taille) || (this.oldDate != this.birthDate)) {
            this.http.post('http://127.0.0.1:5000/user/option/configurer', {
                date_naissance: this.birthDate,
                taille: this.taille

            }).subscribe({

                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.afficheModif();
                },

                error: (err: any) => {
                    // erreurs HTTP (400, 409, 500…)
                    if (err.error && err.error.message) {
                        this.backendResponse = err.error.message; // <- message du backend
                        this.cdr.detectChanges();
                    } else {
                        this.backendResponse = 'Erreur serveur';
                    }
                }
            });
        }
        if (this.oldUsername != this.username) {
            this.http.post('http://127.0.0.1:5000//user/option/modifierUsername', {
                username: this.username
            }).subscribe({

                next: (res: any) => {
                    console.log('RESPONSE OK', res);
                    this.afficheModif();

                },

                error: (err: any) => {
                    // erreurs HTTP (400, 409, 500…)
                    if (err.error && err.error.message) {
                        this.backendResponse = err.error.message; // <- message du backend
                        this.cdr.detectChanges();
                    } else {
                        this.backendResponse = 'Erreur serveur';
                    }
                }
            });
        }
    }



    afficheModif() {
        this.backendResponse = "Modifications appliquées";
        this.cdr.detectChanges();
    }

    supprimer() {
        const confirmAction = confirm("Voulez-vous vraiment supprimer votre compte ?");

        if (confirmAction) {

            this.http.delete('http://127.0.0.1:5000/user/supprimer', {})
                .subscribe({

                    next: (res: any) => {
                        console.log('RESPONSE OK', res);
                        localStorage.removeItem("access_token");
                        this.router.navigate(['']);
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

    resetNotif() {
        this.not.reset(this, this.cdr);
    }
}


