import { Component } from '@angular/core';
import { NgbCarouselModule } from '@ng-bootstrap/ng-bootstrap';
import { CommonModule } from '@angular/common';
import { Notification } from '../notification';
import { Erreur } from '../erreur';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';


@Component({
    selector: 'app-routine-pre-faite',
    imports: [RouterModule, NgbCarouselModule, CommonModule],
    templateUrl: './routine-pre-faite.html',
    styleUrl: './routine-pre-faite.css',
})
export class RoutinePreFaite {

    currentSlide = 0; // index ou id de la slide active
    backendResponse = ""
    routines : any[] = [];

    constructor(private not: Notification, private cdr: ChangeDetectorRef, private http: HttpClient, private erreur: Erreur) { }

    ngOnInit() {
        this.chargerRoutines();
    }
    
    slideChanged() {
        this.resetNotif();
    }

    chargerRoutines() {
        this.http.get('http://127.0.0.1:5000/routine/getRoutinesPrefaites'
            ).subscribe({
                next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.routines = res.routines;
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    ajouterRoutine(carousel: any) {
        // `carousel.activeId` contient l'id de la slide active
        const index = Number(carousel.activeId);
        console.log('Ajouter cette routine:', index);
        this.resetNotif();

        this.http.post('http://127.0.0.1:5000/routine/ajouterRoutinePrefaite', {
            routine: index
        }).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }

}

