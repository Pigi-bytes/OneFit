import { Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EnvoyerElt } from '../envoyerElt';
import { Notification } from '../notification';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Component({
    selector: 'app-affiche-sceance',
    imports: [FormsModule, CommonModule, RouterModule],
    templateUrl: './affiche-sceance.html',
    styleUrls: ['./affiche-sceance.css'],
})
export class AfficheSceance implements OnInit {

    private subscription?: Subscription;
    private platformId = inject(PLATFORM_ID);
    jour: string | null = "";
    exercices: any[] = [];
    backendResponse = "";

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private net: Notification,
        private ei: EnvoyerElt,
        private router: Router,

    ) { }

    ngOnInit() {

        if (isPlatformBrowser(this.platformId)) {
            this.jour = localStorage.getItem("jour");
            this.chargeSeance();

        }

        // récupère le paramètre 'id' de la route

    }

    chargeSeance() {
        console.log("test");
    }

    modifierExo(id: any) {

    }

    supprimer(id: any) {

    }

    ajouterExo() {
        this.router.navigate(['/exercices']);
    }
}