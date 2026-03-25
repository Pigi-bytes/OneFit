import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Location } from '@angular/common';

@Component({
    selector: 'app-compliance',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './compliance.html',
    styleUrl: './compliance.css',
})
export class Compliance {
    constructor(private location: Location) {}

    onBack(): void {
        this.location.back();
    }
}
