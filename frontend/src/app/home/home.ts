import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Theme } from '../theme';

// Composant de la page d'accueil principale
@Component({
    selector: 'app-home',
    imports: [RouterModule],
    standalone: true,
    templateUrl: './home.html',
    styleUrl: './home.css',
})
export class Home implements OnInit {

    constructor(private theme: Theme) { }

    isDark = false;

    /**
     * Initialise le composant : vérifie le thème sombre
     */
    ngOnInit() {
        this.isDark = this.theme.isItDark();
    }

}
