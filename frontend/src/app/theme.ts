import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class Theme {

  isItDark() {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem('darkMode') === 'true';
    }
    return false;
  }

  toggleDark() {
    document.body.classList.toggle('dark');
  }
}
