import { Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { Message } from '../../message';
import { TooltipMoveDirective } from '../tooltipmove';

@Component({
	selector: 'app-exercice-en-cours',
	imports: [FormsModule, CommonModule, RouterModule, TooltipMoveDirective],
	templateUrl: './exercice-en-cours.html',
	styleUrl: './exercice-en-cours.css',
})
export class ExerciceEnCours {
	
    jour: string | null = "";
    private platformId = inject(PLATFORM_ID);
    exo: any;
    backendResponse = "";
	seance_exercise_id = 2;

	constructor(
		private http: HttpClient,
		private cdr: ChangeDetectorRef,
		private router: Router,
	) { }

	ngOnInit(){
		if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            this.chargerExo();
        }
        this.cdr.detectChanges();
	}

	chargerExo(){
		this.http.post('http://127.0.0.1:5000/sport/getSeanceDuJour', {
            routine_id: -1,
            day: this.jour

        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exo = res.seance.exercises.find((e: { seance_exercise_id: any; }) => e.seance_exercise_id === this.seance_exercise_id) ?? null;
                this.backendResponse = res.message;
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

	range(n: number) {
		return Array.from({ length: n }, (_, i) => i + 1);
	}
}
