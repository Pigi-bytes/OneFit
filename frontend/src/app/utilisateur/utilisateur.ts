import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-utilisateur',
  imports: [FormsModule, RouterModule],
  templateUrl: './utilisateur.html',
  styleUrl: './utilisateur.css',
})
export class Utilisateur {

  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);

  username = '';
  password = '';
  backendResponse = '';
  taille = '';
  Busername = '';
  Btaille = '';
  birthDate = '';
  BbirthDate = '';

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.getAllinformation();
    }
  }

  getAllinformation() {
    this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
      this.Busername = res.username;
      this.Btaille = res.taille;
      this.birthDate = res.date_naissance;
      console.log('User:', res);

    });
  }

  modif() {

  }


}
