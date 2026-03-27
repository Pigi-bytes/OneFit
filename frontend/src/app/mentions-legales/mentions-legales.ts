import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Location } from '@angular/common';

@Component({
    selector: 'app-mentions-legales',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './mentions-legales.html',
    styleUrl: './mentions-legales.css',
})
export class MentionsLegales {
    constructor(private location: Location) {}

    onBack(): void {
        this.location.back();
    }
}
