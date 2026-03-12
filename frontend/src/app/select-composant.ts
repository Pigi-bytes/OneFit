import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class SelectComposant {
    private selectComposant = new Subject<number>();
    selectComposant$ = this.selectComposant.asObservable();

    chosirComposant(id: number) {
        this.selectComposant.next(id);
    }

}

