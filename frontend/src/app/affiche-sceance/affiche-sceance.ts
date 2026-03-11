import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EnvoyerElt } from '../envoyerElt';
import { CommonModule } from '@angular/common';
import { Notification } from '../notification';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-affiche-sceance',
    imports: [FormsModule, CommonModule],
    templateUrl: './affiche-sceance.html',
    styleUrl: './affiche-sceance.css',
})
export class AfficheSceance {

    private subscription?: Subscription;

    constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private net: Notification, private ei: EnvoyerElt) { }


    jour = "";


    ngOnInit() {
        this.subscription = this.ei.afficheExercice$.subscribe((jour) => {
            this.jour = jour;

            this.chargeSeance();
        });

    }


    chargeSeance() {

    }


}
