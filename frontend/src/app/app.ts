import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Theme } from './theme';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet], 
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('OneFit');
  constructor (private theme: Theme){}

  ngOnInit() {
    if(this.theme.isItDark()) {
      document.body.classList.add('dark');
    }
  }

}

