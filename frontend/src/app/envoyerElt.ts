import { Injectable } from '@angular/core';
import { ReplaySubject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerElt {
    private afficheExercice = new ReplaySubject<any[]>(1);;
    afficheExercice$ = this.afficheExercice.asObservable();

    triggerRefresh(id: any) {
        this.afficheExercice.next(id);
    }

}
