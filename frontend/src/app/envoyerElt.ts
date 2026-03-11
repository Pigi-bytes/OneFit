import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerElt {
    private afficheExercice = new Subject<any>();
    afficheExercice$ = this.afficheExercice.asObservable();

    private routineActivated = new Subject<any>();
    routineActivated$ = this.routineActivated.asObservable();

    triggerRefresh(id: any) {
        this.afficheExercice.next(id);
    }

    triggerRoutineActivated() {
        this.routineActivated.next(null);
    }

}
