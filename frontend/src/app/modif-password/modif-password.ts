import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Notification } from '../notification';


@Component({
    selector: 'app-modif-password',
    imports: [RouterModule, FormsModule, CommonModule],
    templateUrl: './modif-password.html',
    styleUrl: './modif-password.css',
})
export class ModifPassword {

    oldPassword = '';
    password = '';
    confirmPassword = '';
    backendResponse = '';

    private http = inject(HttpClient);

    constructor(private cdr: ChangeDetectorRef, private not: Notification) { }

    modif() {

        if (this.password !== this.confirmPassword.trim()) {
            this.backendResponse = 'Les mots de passe ne correspondent pas';
            return;
        }

        if (this.password == this.oldPassword) {
            this.backendResponse = 'Les mots de passe sont identiques';
            return;

        }

        this.http.post('http://127.0.0.1:5000//user/option/modifierMDP', {
            password: this.oldPassword,
            new_password: this.password

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = "Modifications appliquées";
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







}
