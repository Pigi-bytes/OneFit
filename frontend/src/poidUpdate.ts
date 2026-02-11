import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
        providedIn: 'root'
})
export class poidUpdate {
        private refreshGraph = new Subject<void>();
        refreshGraph$ = this.refreshGraph.asObservable();

        triggerRefresh() {
                this.refreshGraph.next();
        }
}