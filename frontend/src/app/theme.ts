import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class Theme {

    private platformId = inject(PLATFORM_ID);
    private themeChangeSource = new Subject<boolean>();

    themeChange$ = this.themeChangeSource.asObservable();

    isItDark() {
        if (!isPlatformBrowser(this.platformId)) {
            return false;
        }

        return localStorage.getItem('darkMode') === 'true';
    }

    toggleDark() {
        if (!isPlatformBrowser(this.platformId)) return;

        document.body.classList.toggle('dark');

        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('darkMode', String(isDark));

        this.themeChangeSource.next(isDark);
    }
}