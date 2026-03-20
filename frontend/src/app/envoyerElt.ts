import { Injectable } from '@angular/core';
import { ReplaySubject, Subject } from 'rxjs';

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
    }

    unblockSeance() {
        this.blocked = false;
    }
}
