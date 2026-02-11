import { Component, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { GraphPoid } from '../graph-poid/graph-poid';
import { poidUpdate } from '../../poidUpdate'


@Component({
  selector: 'app-menu-poid',
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './menu-poid.html',
  styleUrl: './menu-poid.css',
})
export class MenuPoid {

  poid = '';
  pDate = '';
  backendResponse = '';
  note: string | null = null;

  @ViewChild('child') graph!: GraphPoid;


  constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private ser: poidUpdate) { }

  ajouterPoid() {

    if (!this.note || this.note.trim() === '') {
      this.note = null;
    }

    this.http.post('http://127.0.0.1:5000/user/ajouterOuModifierPoids', {
      date: this.pDate,
      poids: this.poid,
      note: this.note
    }).subscribe({
      next: (res: any) => {
        console.log('RESPONSE OK', res);
        this.backendResponse = res.message;
        this.ser.triggerRefresh();
        this.cdr.detectChanges();

      },
      error: (err: any) => {
        //erreur 422
        if (err.error.code == 422 && err.error?.errors) {

          const errorsObj = err.error.errors;
          const messages: string[] = [];

          for (const key in errorsObj) {

            const value = errorsObj[key];
            Object.values(value).forEach(v => {
              if (Array.isArray(v)) messages.push(...v);
              else if (typeof v === 'string') messages.push(v);
              messages.push("\n");
            });
          }



          this.backendResponse = messages.join('\n');
        }
        // erreurs HTTP (400, 409, 500…)
        else if (err.error && err.error.message) {
          this.backendResponse = err.error.message; // <- message du backend
        } else {
          this.backendResponse = 'Erreur serveur';
        }
        this.cdr.detectChanges();
      }
    });
  }

  resetNotif() {
    this.backendResponse = '';
    this.cdr.detectChanges();
  }

}


