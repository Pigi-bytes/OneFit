import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class EnvoyerId {
    private afficheExcercice = new BehaviorSubject<string>('');
    afficheExcercice$ = this.afficheExcercice.asObservable();

    triggerRefresh(id: any) {
        this.afficheExcercice.next(id);
    }

}
