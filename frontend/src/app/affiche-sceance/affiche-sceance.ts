import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EnvoyerElt } from '../envoyerElt';
import { Notification } from '../notification';
import { Subscription } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-affiche-sceance',
    imports: [FormsModule, CommonModule],
    templateUrl: './affiche-sceance.html',
    styleUrls: ['./affiche-sceance.css'],
})
export class AfficheSceance implements OnInit {

    private subscription?: Subscription;
    jour: string = '';
    message: any[] = [];

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef,
        private net: Notification,
        private ei: EnvoyerElt,
        private route: ActivatedRoute
    ) { }

    ngOnInit() {
        // récupère le paramètre 'id' de la route
        this.jour = this.route.snapshot.paramMap.get('id') || 'chargement...';
        this.chargeSeance();
    }

    chargeSeance() {
        console.log(this.jour);
    }
}