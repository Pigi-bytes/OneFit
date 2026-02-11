import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Theme } from '../theme';

@Component({
  selector: 'app-home',
  imports: [RouterModule],
  standalone: true,
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {

  constructor (private theme: Theme){}

  toggleTheme(){
    this.theme.toggleDark();
  }
}
