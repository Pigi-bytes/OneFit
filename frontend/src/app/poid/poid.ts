import { Component } from '@angular/core';
import { GraphPoid } from '../graph-poid/graph-poid';
import { MenuPoid } from '../menu-poid/menu-poid';

@Component({
  selector: 'app-poid',
  imports: [GraphPoid, MenuPoid],
  templateUrl: './poid.html',
  styleUrl: './poid.css',
})
export class Poid {

}
