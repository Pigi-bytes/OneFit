import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-routine',
    imports: [FormsModule, CommonModule, RouterModule],
    templateUrl: './routine.html',
    styleUrl: './routine.css',
})
export class Routine {

    constructor(private http: HttpClient, private not: Notification, private cdr: ChangeDetectorRef) { }


    seance = []
    backendResponse = ""
    id = -1;
    message: string[][] = [];



    ngOnInit() {
        this.initMessage();
        this.http.post('http://127.0.0.1:5000/sport/getSeancesPrevu', {
            routine_id: this.id,

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);

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
                else if (err.status == 404 && err.error.errors) {

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

    initMessage() {
        for (let i = 0; i < 7; i++) {
            if (!this.message[i]) {
                this.message[i] = [];
            }
            this.message[i].push("jour de repos");

        }
    }


}
