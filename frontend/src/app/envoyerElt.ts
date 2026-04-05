import { ReplaySubject, BehaviorSubject } from 'rxjs';
import { Injectable, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';


@Injectable({
    providedIn: 'root',
})
export class EnvoyerElt {
    private afficheExercice = new ReplaySubject<any[]>(1);
    private commencerSeance = new ReplaySubject<void>(1);
    private exercicesSubject = new ReplaySubject<any[]>(1);

    private platformId = inject(PLATFORM_ID);

    private blocked: boolean = false;
    private exerciceBlocked: boolean = true;

    afficheExercice$ = this.afficheExercice.asObservable();
    commencerSeance$ = this.commencerSeance.asObservable();
    exercices$ = this.exercicesSubject.asObservable();

    private exercices: any[] = []; // tableau interne


    constructor() {
        // charger depuis le localStorage si présent
        if (isPlatformBrowser(this.platformId)) {
            const saved = localStorage.getItem('exercices');
            if (saved) {
                this.exercices = JSON.parse(saved);
                this.exercicesSubject.next([...this.exercices]);
            }
        }


    }


    triggerRefresh(id: any) {
        this.afficheExercice.next(id);
    }

    startSeance() {
        if (!this.blocked) {
            this.commencerSeance.next();
        }

    }

    blockSeance() {
        this.blocked = true;
        this.commencerSeance = new ReplaySubject<void>(1);
        this.commencerSeance$ = this.commencerSeance.asObservable();
    }

    unblockSeance() {
        this.blocked = false;
    }

    reset() {
        this.afficheExercice = new ReplaySubject<any[]>(1);
        this.afficheExercice$ = this.afficheExercice.asObservable();
    }

    addExercice(exo: any) {
        this.exercices.push(exo);
        this.save();

    }

    soumettre() {
        if (!this.exerciceBlocked) {
            this.exercicesSubject.next([...this.exercices]);
        }

    }

    blockExercice() {
        this.exerciceBlocked = true;
    }

    unblockExercice() {
        this.exerciceBlocked = false;
    }

    resetExercice() {
        this.exercices = [];
        if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('exercices');
        }
        this.exercicesSubject.next([...this.exercices]);
    }

    private save() {
        if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem('exercices', JSON.stringify(this.exercices));
        }
    }
}
