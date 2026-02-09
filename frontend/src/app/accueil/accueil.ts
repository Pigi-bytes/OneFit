import { Component, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-accueil',
  imports: [],
  templateUrl: './accueil.html',
  styleUrl: './accueil.css',
})
export class Accueil {
  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);

  name = "";

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.getUserName();
    }
  }

  getUserName() {
    this.http.get<any>('http://127.0.0.1:5000/user/user').pipe(take(1)).subscribe(res => {
      this.name = res.username;
      console.log('User:', res);
    });
  }
}