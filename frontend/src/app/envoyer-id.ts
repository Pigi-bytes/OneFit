import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerId {
    private afficheExcercice = new Subject<string>();
    afficheExcercice$ = this.afficheExcercice.asObservable();

    triggerRefresh(id: string) {
        this.afficheExcercice.next(id);
    }

}
