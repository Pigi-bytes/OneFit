import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
    providedIn: 'root',
})
export class Theme {

    private platformId = inject(PLATFORM_ID);

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
    }
}
