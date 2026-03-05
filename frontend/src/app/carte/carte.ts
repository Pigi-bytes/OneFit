import { Component, AfterViewInit, Inject, PLATFORM_ID, ViewEncapsulation } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';


@Component({
    selector: 'app-carte',
    standalone: true,
    imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
    templateUrl: './carte.html',
    styleUrl: './carte.css',
    encapsulation: ViewEncapsulation.None
})


export class Carte implements AfterViewInit {

    private map!: L.Map;
    private L!: typeof import('leaflet');

    ville = "";
    backendResponse = "";

    constructor(@Inject(PLATFORM_ID) private platformId: Object, private not: Notification, private cdr: ChangeDetectorRef, private http: HttpClient) { }

    async ngAfterViewInit(): Promise<void> {
        if (isPlatformBrowser(this.platformId)) {

            this.L = await import('leaflet');

            this.map = this.L.map('map').setView([47.988, 0.160], 13);

            this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(this.map);

            /* GEOLOCALISATION, WIP
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition((position: Position) => console.log(position));
                  }
            */

            const triggerTabList = document.querySelectorAll('[data-bs-toggle="tab"]');

        }
    }
    trouverLoc() {
        console.log("HTTP:", this.http);

        this.http.post('http://127.0.0.1:5000/user/option/salle', {
            ville: this.ville,
        }).subscribe({

            next: async (res: any) => {
                console.log('RESPONSE OK', res);


                res.results.forEach((salle: any) => {
                    const lat = salle.latitude;
                    const lng = salle.longitude;
                    const name = salle.name || 'N/A';
                    const adresse = salle.location.address || 'N/A';
                    const tel = salle.tel || 'N/A';
                    const mail = salle.mail || 'N/A';
                    const webSite = salle.website || 'N/A';
                    const customIcon = this.L.icon({
                        iconUrl: `${salle.categories[0].icon.prefix}64${salle.categories[0].icon.suffix}`,
                        iconSize: [64, 64], // taille de l'icône
                        iconAnchor: [16, 32], // point de l'icône qui correspond à la position du marker
                        popupAnchor: [0, -32] // point d'où le popup s'ouvre
                    });


                    this.L.marker([lat, lng], { icon: customIcon }).addTo(this.map).bindPopup(`<ul>
                        <li>nom : ${name}</li>
                        <li>adresse :${adresse}</li>
                        <li>téléphone :${tel}</li>
                        <li>mail : ${mail}</li>
                        <li>site : ${webSite}</li>
                        </ul>`);
                });

                const group = this.L.featureGroup(
                    res.results.map((salle: any) => this.L.marker([salle.latitude, salle.longitude]))
                );
                this.map.fitBounds(group.getBounds(), { padding: [50, 50] });

                this.cdr.detectChanges();
            },


            error: (err: any) => {
                //erreur 422
                if (err.status == 422 && err.error.errors) {

                    const errorsObj = err.error.errors;
                    const messages: string[] = [];



                    for (const key in errorsObj) {

                        const value = errorsObj[key];
                        Object.values(value).forEach(v => {
                            if (Array.isArray(v)) messages.push(...v);
                            else if (typeof v === 'string') messages.push(v);
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
        this.not.reset(this, this.cdr);
    }
}