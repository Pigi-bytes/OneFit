import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { Theme } from './theme';
import { SideMenu } from './side-menu/side-menu';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, SideMenu],
    templateUrl: './app.html',
    styleUrl: './app.css'
})
export class App implements OnInit {



    protected readonly title = signal('OneFit');
    showMenu = true;

    constructor(private theme: Theme, private router: Router) {
        this.router.events.subscribe(() => {
            let route = this.router.routerState.snapshot.root;

            while (route.firstChild) {
                route = route.firstChild;
            }

            this.showMenu = !route.data?.['hideMenu'];
        });
    }

    ngOnInit() {
        if (this.theme.isItDark()) {
            const page = document.querySelector('.layout');
            if (page)
                page.classList.toggle('dark');
        }
    }

}

