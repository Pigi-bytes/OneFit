import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt';
import { TooltipMoveDirective } from '../tooltipmove';


@Component({
    selector: 'app-routine',
    imports: [FormsModule, CommonModule, RouterModule, TooltipMoveDirective],
    templateUrl: './routine.html',
    styleUrl: './routine.css',
})
export class Routine {

    constructor(private http: HttpClient, private not: Notification, private cdr: ChangeDetectorRef, private elt: EnvoyerElt, private router: Router) { }


    seance = []
    backendResponse = ""
    id = -1;
    message: any[] = [];

    seances: any[] = [];



    ngOnInit() {

        this.http.post('http://127.0.0.1:5000/sport/getSeancesPrevu', {
            routine_id: this.id,

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);

                this.seances = res.seances.map((s: any) => ({
                    jour: s.day,
                    title: s.title,
                    exercises: s.exercises,
                    isRestDay: s.is_rest_day
                }));

                this.message = [];


                let i = 0;
                for (let s of this.seances) {
                    this.message[i] = [];

                    if (s.exercises.length === 0) {
                        this.message[i].push(s.title);
                    }

                    else {
                        for (let m of s.exercises) {
                            this.message[i].push(m.name + "<br>" + " <span class='text-gray'>" + m.planned_sets + " sets de " + m.planned_reps + " reps à " + m.planned_weight + " kg</spam>");
                        }
                    }

                    i += 1;

                }

                this.cdr.detectChanges();



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


    afficherSeance(id: string) {

        localStorage.setItem("jour", id);
        this.elt.triggerRefresh([5]);
        this.router.navigate(['/seance']);

    }

}
