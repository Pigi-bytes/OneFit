import { Component, inject, PLATFORM_ID, ViewEncapsulation } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule, Router } from '@angular/router';
import { Theme } from '../theme';

@Component({
    selector: 'app-side-menu',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './side-menu.html',
    styleUrl: './side-menu.css',
    encapsulation: ViewEncapsulation.None,
})
export class SideMenu {
    private http = inject(HttpClient);
    private platformId = inject(PLATFORM_ID);
    private router = inject(Router);
    isDark = false;

    constructor(private theme: Theme) { }
    name = "";

    ngOnInit() {
        this.isDark = this.theme.isItDark();
    }

    deconnexion() {
        const confirmAction = confirm("Êtes-vous sûr(e) de vouloir vous déconnecter ?");

        if (confirmAction) {
            localStorage.removeItem("access_token")
            this.router.navigate(['']);
        }
    }

    toggleTheme() {
        this.theme.toggleDark();
        this.isDark = this.theme.isItDark();
    }
}
