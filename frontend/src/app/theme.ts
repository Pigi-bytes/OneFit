import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class Theme {
  toggleDark() {
    document.body.classList.toggle('dark');
  }
}
