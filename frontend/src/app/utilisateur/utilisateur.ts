import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-utilisateur',
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './utilisateur.html',
  styleUrl: './utilisateur.css',
})
export class Utilisateur {

  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);

  username = '';
  backendResponse = '';
  taille = '';
  Busername = '';
  birthDate = '';

  private oldUsername = '';
  private oldDate = '';
  private oldTaille = '';

  constructor(private router: Router, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.getAllinformation();
    }
  }

  getAllinformation() {
    this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
      this.username = res.username;
      this.taille = res.taille;
      this.birthDate = res.date_naissance;

      this.oldUsername = this.username;
      this.oldDate = this.birthDate;
      this.oldTaille = this.taille
      console.log('User:', res);

    });

  }

  modif() {

    var motif = false;

    if ((this.oldTaille != this.taille) || (this.oldDate != this.birthDate)) {
      this.http.post('http://127.0.0.1:5000/user/option/configurer', {
        date_naissance: this.birthDate,
        taille: this.taille

      }).subscribe({

        next: (res: any) => {
          console.log('RESPONSE OK', res);
          this.afficheModif();
        },

        error: (err: any) => {
          // erreurs HTTP (400, 409, 500…)
          if (err.error && err.error.message) {
            this.backendResponse = err.error.message; // <- message du backend
            this.cdr.detectChanges();
          } else {
            this.backendResponse = 'Erreur serveur';
          }
        }
      });
    }
    if (this.oldUsername != this.username) {
      this.http.post('http://127.0.0.1:5000//user/option/modifierUsername', {
        username: this.username
      }).subscribe({

        next: (res: any) => {
          console.log('RESPONSE OK', res);
          this.afficheModif();

        },

        error: (err: any) => {
          // erreurs HTTP (400, 409, 500…)
          if (err.error && err.error.message) {
            this.backendResponse = err.error.message; // <- message du backend
            this.cdr.detectChanges();
          } else {
            this.backendResponse = 'Erreur serveur';
          }
        }
      });
    }
  }

  afficheModif() {
    this.backendResponse = "Modifications appliquées";
    this.cdr.detectChanges();
  }
}


