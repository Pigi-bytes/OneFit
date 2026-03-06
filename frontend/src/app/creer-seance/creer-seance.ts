import { Component } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-creer-seance',
    imports: [FormsModule, HttpClientModule, CommonModule],
    templateUrl: './creer-seance.html',
    styleUrl: './creer-seance.css',
})
export class CreerSeance {
    backendResponse = "";
    nom = "";

    constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef, private not: Notification) { }

    trouverExo() { }


    resetNotif() {
        this.not.reset(this, this.cdr);
    }

}