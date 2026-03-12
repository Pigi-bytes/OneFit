import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerElt {
    private afficheExercice = new Subject<any>();
    afficheExercice$ = this.afficheExercice.asObservable();

    triggerRefresh(id: any) {
        this.afficheExercice.next(id);
    }

}
