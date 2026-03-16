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
import { AjouterExo } from './ajouter-exo/ajouter-exo';
import { AfficherExo } from './afficher-exo/afficher-exo';
import { Exercices } from './exercices/exercices';
import { Routine } from './routine/routine';
import { ChoisirRoutine } from './choisir-routine/choisir-routine';
import { RoutinesPersos } from './routines-persos/routines-persos';
import { Seance } from './seance/seance';
import { ExerciceEnCours } from './exercice-en-cours/exercice-en-cours';
import { AfficheSceance } from './afficher-seance/afficher-seance';

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
    { path: "ajouter-exo", component: AjouterExo },
    { path: "afficher-exo", component: AfficherExo },
    { path: "exercices", component: Exercices },
    { path: "routine", component: Routine },
    { path: "choisir-routine", component: ChoisirRoutine },
    { path: "routines-persos", component: RoutinesPersos },
    { path: "seance", component: Seance },
    { path: "exercice-en-cours", component: ExerciceEnCours },
    { path: "afficher-seance", component: AfficheSceance },
];
