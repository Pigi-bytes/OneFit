import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-creer-compte',
  standalone: true,
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './creer-compte.html',
  styleUrl: './creer-compte.css',
})
export class CreerCompte {

  username = '';
  password = '';
  backendResponse = '';

  constructor(private http: HttpClient, private router: Router) { }

  creer() {
    this.http.post('http://127.0.0.1:5000/auth/inscription', {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (res: any) => {
        this.backendResponse = res.message;
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
