import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { EnvoyerElt } from '../envoyerElt'
import { Subscription } from 'rxjs';
import { TooltipMoveDirective } from '../tooltipmove';
import { Erreur } from '../erreur';

@Component({
    selector: 'app-choisir-routine',
    imports: [CommonModule, RouterModule, TooltipMoveDirective],
    templateUrl: './choisir-routine.html',
    styleUrl: './choisir-routine.css',
})

export class ChoisirRoutine {
    backendResponse = "";
    routines: any[] = [];
    private subscription?: Subscription;

    constructor(private http: HttpClient, private router: Router, private erreur: Erreur, private cdr: ChangeDetectorRef, private not: Notification, private ei: EnvoyerElt) { }

    ngOnInit() {
        this.getRoutines();
        this.subscription = this.ei.afficheExercice$.subscribe(() => {
            this.getRoutines();
        });
    }

    getRoutines() {
        this.http.get('http://127.0.0.1:5000/routine/getRoutines', {}).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.routines = res.routines.map((r: any) => ({
                    nom: r["name"],
                    id: r["id"],
                    isActive: r["is_active"],
                }));

                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    AfficherInfosRoutine(id: any) {
        console.log(id);
        this.ei.triggerRefresh(id);
    }

    creerRoutine(){
        this.http.post('http://127.0.0.1:5000/routine/createRoutine', {
            name: "Nouvelle Routine"
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.cdr.detectChanges();
                this.getRoutines();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }
}