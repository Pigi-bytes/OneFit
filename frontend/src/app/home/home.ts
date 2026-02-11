import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Theme } from '../theme';

@Component({
  selector: 'app-home',
  imports: [RouterModule],
  standalone: true,
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  isDark = false;
  constructor (private theme: Theme){}

  ngOnInit() {
    if (typeof localStorage !== 'undefined') {
      if(localStorage.getItem('darkMode') === 'true'){
        document.body.classList.add('dark');
      }
    }
  }

  toggleTheme(){
    this.theme.toggleDark();
    this.isDark = document.body.classList.contains('dark');

    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('darkMode', String(this.isDark));
    }
  }
}
