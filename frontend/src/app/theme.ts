import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class Theme {

  isItDark() {
    return localStorage.getItem('darkMode') === 'true';
  }

  toggleDark() {
    document.body.classList.toggle('dark');
  }
}
