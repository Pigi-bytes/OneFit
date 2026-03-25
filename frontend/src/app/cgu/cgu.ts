import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Location } from '@angular/common';

@Component({
    selector: 'app-cgu',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './cgu.html',
    styleUrl: './cgu.css',
})

export class Cgu {
  constructor(private location: Location) {}

  onBack(): void {
    this.location.back();
  }
}
