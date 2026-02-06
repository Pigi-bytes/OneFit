import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Connexion } from './connexion/connexion';
import { CreerCompte } from './creer-compte/creer-compte';
import { ConfigurerCompte } from './configurer-compte/configurer-compte';

export const routes: Routes = [
        { path: '', component: Home },
        { path: "connexion", component: Connexion },
        { path: "creer-compte", component: CreerCompte },
        { path: "configurer-compte", component: ConfigurerCompte },
];
