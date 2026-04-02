import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt';
import { Message } from '../../message';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-routine',
    imports: [FormsModule, CommonModule, RouterModule],
    templateUrl: './routine.html',
    styleUrl: './routine.css',
})
export class Routine {

    constructor(private http: HttpClient, private not: Notification, private erreur: Erreur, private cdr: ChangeDetectorRef, private elt: EnvoyerElt, private router: Router) { }


    seance = []
    backendResponse = ""
    id = -1;
    message: any[] = [];

    seances: any[] = [];


    jours = [
        { short: 'Lun', full: 'Lundi' },
        { short: 'Mar', full: 'Mardi' },
        { short: 'Mer', full: 'Mercredi' },
        { short: 'Jeu', full: 'Jeudi' },
        { short: 'Ven', full: 'Vendredi' },
        { short: 'Sam', full: 'Samedi' },
        { short: 'Dim', full: 'Dimanche' },
    ];
    
    selectedDay = ((new Date().getDay() + 6) % 7);

    selectDay(i: number) {
        this.selectedDay = i;
    }


    ngOnInit() {

        this.http.post('http://127.0.0.1:5000/seance/getSeancesPrevu', {
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

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }


    afficherSeance(id: string) {

        localStorage.setItem("jour", id);
        this.elt.triggerRefresh([Message.RESET_CONFIGURATEUR]);
        this.router.navigate(['/seance']);

    }

}
