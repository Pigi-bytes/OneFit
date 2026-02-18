import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';

@Component({
    selector: 'app-connexion',
    standalone: true,
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './connexion.html'
})
export class Connexion {
    username = '';
    password = '';
    backendResponse = '';

    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification) { }

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

            error: (err: any) => {
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
                else if (err.error && err.error.message) {
                    this.backendResponse = err.error.message; // message backend
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
}
