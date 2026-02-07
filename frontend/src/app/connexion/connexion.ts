import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-connexion',
  standalone: true,
  imports: [RouterModule, FormsModule],
  templateUrl: './connexion.html'
})
export class Connexion {
  username = '';
  password = '';

  constructor(private http: HttpClient, private router: Router) { }

  login() {
    this.http.post('http://127.0.0.1:5000/auth/login', {
      username: this.username,
      password: this.password
    }).subscribe((res: any) => {
      console.log('Réponse du backend:', res);

      if (res.access_token) {

        localStorage.setItem('access_token', res.access_token);

        this.http.get('http://127.0.0.1:5000/user/user').subscribe(res => {
          console.log('User:', res);
        });

        if (res.success) {
          alert('Connexion réussie !');
        }


        this.router.navigate(['/']);
      } else {
        alert('Erreur de connexion');
      }
    });
  }
}
