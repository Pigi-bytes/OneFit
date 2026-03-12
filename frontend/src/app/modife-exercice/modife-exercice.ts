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
    selector: 'app-modife-exercice',
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './modife-exercice.html',
    styleUrl: './modife-exercice.css',
})
export class ModifeExercice {

    setNumber = null;
    repNumber = null;
    poids = null;
    backendResponse = "";


    constructor(private http: HttpClient, private not: Notification, private cdr: ChangeDetectorRef, private elt: EnvoyerElt) { }

    private subscription?: Subscription;

    affiche: any | null = null;
    exo: string | null = null;


    ngOnInit() {
        this.exo = null;
        this.subscription = this.elt.afficheExercice$.subscribe((payload) => {
            if (Array.isArray(payload) && payload[0] != 2) {
                const type = payload[0];
                const id = payload[1];

                this.exo = id;

                if (type === 0) {
                    this.affiche = '';       // redirige vers TestComposant
                } else if (type === 1) {
                    this.affiche = null;    // redirige vers AfficherExo
                }

                this.cdr.detectChanges();
            }
        });
    }


    modifier() {

    }


    annuler() {
        this.elt.triggerRefresh([0, null]);
    }

    supprimer() { }


    resetNotif() {
        this.not.reset(this, this.cdr);
    }



}
