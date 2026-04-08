import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { EnvoyerElt } from '../envoyerElt';
import { Message } from '../../message';
import { CommonModule } from '@angular/common';
import { Erreur } from '../erreur';
import { ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-accueil',
    imports: [RouterModule, CommonModule],
    templateUrl: './accueil.html',
    styleUrl: './accueil.css',
})
export class Accueil {
    private http = inject(HttpClient);
    private platformId = inject(PLATFORM_ID);
    private router = inject(Router);
    private elt = inject(EnvoyerElt);
    private cdr = inject(ChangeDetectorRef);
    private erreur = inject(Erreur);


    repos: boolean = false;

    name = "";

    // Calendrier
    today = new Date();

    currentMonth = new Date(this.today.getFullYear(), this.today.getMonth(), 1);



    backendResponse = "";

    allDate: string[] = [];


    /**
     * formatage du mois
     */
    get monthLabel(): string {
        return this.currentMonth.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    }

    /**
     * avoir le nombre de sessions réalisées
     */
    get totalSessions(): number {
        return this.allDate.length;
    }

    /**
     * avoir le nombre de sessions réalisées durant le mois
     */
    get sessionsThisMonth(): number {
        const year = this.currentMonth.getFullYear();
        const month = String(this.currentMonth.getMonth() + 1).padStart(2, '0');
        const prefix = `${year}-${month}-`;
        return this.allDate.filter((date) => typeof date === 'string' && date.startsWith(prefix)).length;
    }

    /**
     * est-ce que la séance a déjà été réalisée
     */
    get didSessionToday(): boolean {
        return this.dejaEffectue();
    }

    /**
     * obtenir le calendrier
     */
    get calendarDays(): (number | null)[] {
        const year = this.currentMonth.getFullYear();
        const month = this.currentMonth.getMonth();
        const firstDay = (new Date(year, month, 1).getDay() + 6) % 7; // lundi = 0
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const days: (number | null)[] = [];
        for (let i = 0; i < firstDay; i++) days.push(null);
        for (let d = 1; d <= daysInMonth; d++) {
            days.push(d);
        }
        return days;
    }

    /**
     * Est-ce que le jour correspond à aujourd'hui
     * @param day le jour
     * @returns true si le jour est aujourd'hui
     */
    isToday(day: number | null): boolean {
        if (!day) return false;
        return day === this.today.getDate()
            && this.currentMonth.getMonth() === this.today.getMonth()
            && this.currentMonth.getFullYear() === this.today.getFullYear();
    }

    /**
     * mois précédent
     */
    prevMonth() {
        this.currentMonth = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() - 1, 1);
    }

    /**
     * mois suivant
     */
    nextMonth() {
        this.currentMonth = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() + 1, 1);
    }

    /**
     * vérifier la streak
     * @param day un jour
     * @returns true si la streak est maintenue
     */
    verifStreak(day: number | null) {
        if (!day) return false;

        const year = this.currentMonth.getFullYear();
        const month = this.currentMonth.getMonth() + 1;
        const dayStr = String(day).padStart(2, '0');
        const monthStr = String(month).padStart(2, '0');

        const date = `${year}-${monthStr}-${dayStr}`;

        return this.allDate.includes(date);
    }

    // initialisation
    ngOnInit() {



        if (isPlatformBrowser(this.platformId)) {
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
            localStorage.removeItem("exoCourrant");
            localStorage.setItem("noRecap", "true");
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.router.navigate(['']);
                alert("Veuillez-vous connecter.");
                return;
            }

            this.getUserName();
            this.getSeance();
        }
        this.recupStrick();
    }

    // récupérer le nom d'utilisateur
    getUserName() {
        this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
            this.name = res.username;
        });
    }

    // se déconnecter
    deconnexion() {
        localStorage.removeItem("access_token");
        this.router.navigate(['']);
    }

    // commencer une séance
    commencerSeance() {
        localStorage.removeItem("seanceEnCours");
        localStorage.removeItem("seanceFini");

        localStorage.removeItem("coteExo");
        localStorage.removeItem("coteRecap");
        localStorage.removeItem("noRecap");
        localStorage.removeItem("seanceJour");
        this.elt.reset();
        this.elt.triggerRefresh([Message.COMMENCER_SEANCE]);
        this.elt.unblockSeance();
        this.elt.startSeance();
        this.router.navigate(['/seance-en-cours']);
    }

    // récupérer la streak
    recupStrick() {
        this.http.get('http://127.0.0.1:5000/user/getStreak', {}).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.allDate = Array.isArray(res['days']) ? res['days'] : [];
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },


            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });
    }

    // est-ce que la séance est déjà effectuée
    dejaEffectue() {

        const d = new Date();

        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');

        const date = `${year}-${month}-${day}`;

        return this.allDate.includes(date);

    }

    // obtenir la séance du jour
    getSeance() {
        this.http.post('http://127.0.0.1:5000/seance/getSeanceDuJour', {
            routine_id: -1,
            day: localStorage.getItem("jour"),

        }).subscribe({
            next: (res: any) => {
                console.log('RESPONSE OK', res.seance.title);

                if (res.seance.title === "Jour de Repos") {

                    this.repos = true;
                }


            },
            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });

    }
}