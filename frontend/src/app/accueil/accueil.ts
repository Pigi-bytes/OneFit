import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';

@Component({
  selector: 'app-accueil',
  imports: [RouterModule],
  templateUrl: './accueil.html',
  styleUrl: './accueil.css',
})
export class Accueil {
  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);
  private router = inject(Router);

  name = "";

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.router.navigate(['']);
        alert("veuillez vous connecter")
        return;
      }
      this.getUserName();
    }
  }

  getUserName() {
    this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
      this.name = res.username;
    });
  }

  deconnexion() {
    localStorage.removeItem("access_token")
    this.router.navigate(['']);

  }
}