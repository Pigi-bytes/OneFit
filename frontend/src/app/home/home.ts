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
  constructor (private theme: Theme){}

  isDark = false;

  ngOnInit() {
    this.isDark = this.theme.isItDark();
    if (typeof localStorage !== 'undefined') {
      if(localStorage.getItem('darkMode') === 'true'){
        document.body.classList.add('dark');
        this.isDark = true;
        
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
