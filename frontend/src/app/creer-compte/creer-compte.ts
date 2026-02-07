import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';


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
  confirmPassword = '';

  constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef) { }

  creer() {

    if (this.password !== this.confirmPassword.trim()) {
      this.backendResponse = 'Les mots de passe ne correspondent pas';
      return;
    }

    this.http.post('http://127.0.0.1:5000/auth/inscription', {
      username: this.username,
      password: this.password

    }).subscribe({
      next: (res: any) => {
        console.log('RESPONSE OK', res);
        this.backendResponse = res.message;
        this.cdr.detectChanges();
        this.router.navigate(['/configurer-compte']);

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
