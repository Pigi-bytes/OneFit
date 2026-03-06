import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Connexion } from './connexion/connexion';
import { CreerCompte } from './creer-compte/creer-compte';
import { ConfigurerCompte } from './configurer-compte/configurer-compte';
import { Accueil } from './accueil/accueil';
import { Utilisateur } from './utilisateur/utilisateur';
import { ModifPassword } from './modif-password/modif-password';
import { Poid } from './poid/poid';
import { Carte } from './carte/carte';
import { SideMenu } from './side-menu/side-menu';
import { CreerSeance } from './creer-seance/creer-seance';

export const routes: Routes = [
    { path: '', component: Home, data: { hideMenu: true } },
    { path: "connexion", component: Connexion, data: { hideMenu: true } },
    { path: "creer-compte", component: CreerCompte, data: { hideMenu: true } },
    { path: "configurer-compte", component: ConfigurerCompte, data: { hideMenu: true } },
    { path: "accueil", component: Accueil },
    { path: "utilisateur", component: Utilisateur },
    { path: "modif-password", component: ModifPassword, data: { hideMenu: true } },
    { path: "poid", component: Poid },
    { path: "carte", component: Carte },
    { path: "side-menu", component: SideMenu },
    { path: "creer-seance", component: CreerSeance },
];
