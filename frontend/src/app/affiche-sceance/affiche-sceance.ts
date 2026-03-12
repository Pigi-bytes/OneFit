import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EnvoyerElt } from '../envoyerElt';
import { Notification } from '../notification';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { App } from '../app';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';

@Component({
    selector: 'app-affiche-sceance',
    imports: [FormsModule, CommonModule, RouterModule],
    templateUrl: './affiche-sceance.html',
    styleUrls: ['./affiche-sceance.css'],
})
export class AfficheSceance implements OnInit {

    private subscription?: Subscription;
    jour: string = '';
    exercices: any[] = [];
    backendResponse = "";

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private net: Notification,
        private ei: EnvoyerElt,
        private app: App,
        private router: Router

    ) { }

    ngOnInit() {
        // récupère le paramètre 'id' de la route
        this.jour = this.app.jourActuel;
        this.chargeSeance();
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