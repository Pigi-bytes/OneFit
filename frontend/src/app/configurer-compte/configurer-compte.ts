import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-configurer-compte',
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './configurer-compte.html',
  styleUrl: './configurer-compte.css',
})
export class ConfigurerCompte {

  height = '';
  birthDate = '';
  backendResponse = '';

  constructor(private http: HttpClient, private router: Router) { }

  configurer() {
    this.http.post('http://127.0.0.1:5000/user/configurer', {
      taille: this.height,
      date_naissance: this.birthDate
    }).subscribe({
      next: (res: any) => {
        this.backendResponse = res.message;

        this.router.navigate(['/accueil']);
      },
      error: (err: any) => {
        // erreurs HTTP (400, 409, 500…)
        if (err.error && err.error.message) {
          this.backendResponse = err.error.message; // <- message du backend
        } else {
          this.backendResponse = 'Erreur serveur';
        }
      }
    });
  }
}
