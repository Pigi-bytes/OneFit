import { Injectable } from '@angular/core';
import { ReplaySubject } from 'rxjs';


@Injectable({
    providedIn: 'root',
})
export class EnvoyerElt {
    private afficheExercice = new ReplaySubject<any[]>(1);
    private commencerSeance = new ReplaySubject<void>(1);
    private blocked: boolean = false;

    afficheExercice$ = this.afficheExercice.asObservable();
    commencerSceance$ = this.commencerSeance.asObservable();

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
        this.commencerSceance$ = this.commencerSeance.asObservable();
    }

    unblockSeance() {
        this.blocked = false;
    }

    reset() {
        this.afficheExercice = new ReplaySubject<any[]>(1);
        this.afficheExercice$ = this.afficheExercice.asObservable();
    }
}
