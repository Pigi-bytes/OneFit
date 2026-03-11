import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerId {
    private afficheExercice = new Subject<string>();
    afficheExercice$ = this.afficheExercice.asObservable();

    triggerRefresh(id: string) {
        this.afficheExercice.next(id);
    }

}
