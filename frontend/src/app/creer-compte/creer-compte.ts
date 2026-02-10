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

        // connexion auto après l'inscription
        this.http.post('http://127.0.0.1:5000/auth/login', {
          username: this.username,
          password: this.password
        }).subscribe((res: any) => {
          localStorage.setItem('access_token', res.access_token);
          this.router.navigate(['/configurer-compte']);
        });
      },

      error: (err: any) => {
        //erreur 422
        if (err.error.code == 422 && err.error?.errors) {

          const errorsObj = err.error.errors;
          const messages: string[] = [];



          for (const key in errorsObj) {

            const value = errorsObj[key];
            Object.values(value).forEach(v => {
              if (Array.isArray(v)) messages.push(...v);
              else if (typeof v === 'string') messages.push(v);
            });
          }

          this.backendResponse = messages.join('\n');
        }
        // erreurs HTTP (400, 409, 500…)
        else if (err.error && err.error.message) {
          this.backendResponse = err.error.message; // <- message du backend
        } else {
          this.backendResponse = 'Erreur serveur';
        }
        this.cdr.detectChanges();
      }
    });

  }

}
