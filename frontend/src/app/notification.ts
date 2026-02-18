import { Injectable } from '@angular/core';
import { ChangeDetectorRef } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class Notification {

    reset(component: { backendResponse: string }, cdr: ChangeDetectorRef) {
        component.backendResponse = "";
        cdr.detectChanges();
    }

}

