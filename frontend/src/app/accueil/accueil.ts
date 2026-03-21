import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { EnvoyerElt } from '../envoyerElt';
import { Message } from '../../message';

@Component({
    selector: 'app-accueil',
    imports: [RouterModule],
    templateUrl: './accueil.html',
    styleUrl: './accueil.css',
})
export class Accueil {
    private http = inject(HttpClient);
    private platformId = inject(PLATFORM_ID);
    private router = inject(Router);
    private elt = inject(EnvoyerElt);

    name = "";

    ngOnInit() {
        if (isPlatformBrowser(this.platformId)) {
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.router.navigate(['']);
                alert("veuillez vous connecter")
                return;
            }
            this.getUserName();
        }
    }

    getUserName() {
        this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
            this.name = res.username;
        });
    }

    deconnexion() {
        localStorage.removeItem("access_token")
        this.router.navigate(['']);
    }

    commencerSeance() {

        localStorage.removeItem("seanceEnCours");
        localStorage.removeItem("seanceFini");
        const now = new Date();
        let jour = "";
        switch (now.getDay()) {
            case 0: jour = "Dimanche"; break;
            case 1: jour = "Lundi"; break;
            case 2: jour = "Mardi"; break;
            case 3: jour = "Mercredi"; break;
            case 4: jour = "Jeudi"; break;
            case 5: jour = "Vendredi"; break;
            case 6: jour = "Samedi"; break;
        }

        localStorage.setItem("jour", jour);
        localStorage.removeItem("coteExo");
        localStorage.removeItem("coteRecap");
        this.elt.reset();
        this.elt.triggerRefresh([Message.COMMENCER_SEANCE]);
        this.elt.unblockSeance();
        this.elt.startSeance();
        this.router.navigate(['/seance-en-cours']);
    }
}