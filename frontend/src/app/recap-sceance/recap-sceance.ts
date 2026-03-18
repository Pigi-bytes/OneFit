import { Component, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { ChangeDetectorRef } from '@angular/core';
import { Chrono } from '../chrono/chrono';
import { Message } from '../../message';
import { EnvoyerElt } from '../envoyerElt';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Component({
    selector: 'app-recap-sceance',
    imports: [Chrono, RouterModule],
    templateUrl: './recap-sceance.html',
    styleUrl: './recap-sceance.css',
})
export class RecapSceance {
    name: any
    private platformId = inject(PLATFORM_ID);

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ei: EnvoyerElt, private route: Router) { }


    ngOnInit() {
        this.ei.triggerRefresh([Message.CHRONO_RECAP]);
        if (isPlatformBrowser(this.platformId)) {
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.route.navigate(['']);
                alert("veuillez vous connecter")
                return;
            }
            this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
                this.name = res.username;
            });
        }

        this.cdr.detectChanges();
    }

    terminer() {
        this.ei.triggerRefresh([Message.FINIR_RECAP]);
        this.route.navigate(['/accueil']);

    }


}
