import { Component, AfterViewInit, Inject, PLATFORM_ID, ViewEncapsulation } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Notification } from '../notification';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Theme } from '../theme';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';


@Component({
    selector: 'app-carte',
    standalone: true,
    imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
    templateUrl: './carte.html',
    styleUrl: './carte.css',
    encapsulation: ViewEncapsulation.None
})


export class Carte implements AfterViewInit {
    private themeSubscription?: Subscription;

    private map!: L.Map;
    private L!: typeof import('leaflet');
    private currentTileLayer?: L.TileLayer;

    ville = "";
    backendResponse = "";


    markers: L.Marker[] = [];
    couleur = '#b83100';

    constructor(@Inject(PLATFORM_ID) private platformId: Object, private not: Notification, private cdr: ChangeDetectorRef, private http: HttpClient, private theme: Theme) { }

    async ngAfterViewInit(): Promise<void> {
        this.themeSubscription = this.theme.themeChange$.subscribe(() => {
            this.updateChartColors();
        });

        if (isPlatformBrowser(this.platformId)) {

            const isDark = localStorage.getItem('darkMode') === 'true';
            let themeMap = 'alidade_smooth';

            if (isDark) {
                themeMap = 'alidade_smooth_dark';
                this.couleur = '#aba3a3ff';

            }



            this.L = await import('leaflet');

            this.map = this.L.map('map').setView([47.988, 0.160], 13);

            this.L.tileLayer('https://tiles.stadiamaps.com/tiles/' + themeMap + '/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; Stadia Maps, &copy; OpenStreetMap contributors'
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
        const myCustomColour = 'red';

        const markerHtmlStyles = `
            background-color: ${myCustomColour};
     `
        console.log("HTTP:", this.http);

        this.http.post('http://127.0.0.1:5000/externe/salle', {
            ville: this.ville,
        }).subscribe({

            next: async (res: any) => {
                console.log('RESPONSE OK', res);

                this.afficherPoint(res);

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
    findByLoc() {
        const center = this.map.getCenter();

        this.http.post('http://127.0.0.1:5000/externe/salleByLoc', {
            lat: center.lat,
            lng: center.lng
        }).subscribe({

            next: async (res: any) => {
                console.log('RESPONSE OK', res);



                this.afficherPoint(res);

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

    afficherPoint(res: any) {
        this.deleteMarker();
        res.results.forEach((salle: any) => {
            const lat = Number(salle.latitude);
            const lng = Number(salle.longitude);
            const name = salle.name || 'N/A';
            const adresse = salle.location.address || 'N/A';
            const tel = salle.tel || 'N/A';
            const mail = salle.mail || 'N/A';
            const webSite = salle.website || 'N/A';
            const customIcon = this.L.divIcon({
                className: '',
                html: `<div style="
                            width: 64px; height: 64px; 
                            background-color: ${this.couleur};
                            -webkit-mask-image: url('${salle.categories[0].icon.prefix}64${salle.categories[0].icon.suffix}');
                            mask-image: url('${salle.categories[0].icon.prefix}64${salle.categories[0].icon.suffix}');
                            background-size: cover;
                        "></div>`,
                iconSize: [64, 64],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            });

            const mailHtml = mail !== 'N/A' ? `<li> mail : ${mail} </li>` : '';
            const addressHtml = adresse !== 'N/A' ? `<li>adresse : ${adresse} </li>` : '';
            const telHtml = tel !== 'N/A' ? `<li> téléphone :${tel} </li>` : '';
            const siteHtml = webSite !== 'N/A' ? `<li> site :${webSite} </li>` : '';


            const marker = this.L.marker([lat, lng], { icon: customIcon }).addTo(this.map).bindPopup(`<ul>
                        <li>nom : ${name} </li>
                        ${addressHtml}
                        ${telHtml}
                        ${mailHtml}
                        ${siteHtml}
                         </ul>`);

            this.markers.push(marker);
        });

        if (this.markers.length === 1) {
            this.map.setView(this.markers[0].getLatLng(), 14);
        } else {
            const bounds = this.L.latLngBounds([]);
            this.markers.forEach(m => bounds.extend(m.getLatLng()));
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }

    }

    private async updateChartColors() {
        if (!this.map || !this.L) return;

        const isDark = this.theme.isItDark();

        this.couleur = isDark ? '#aba3a3ff' : '#b83100';
        const themeMap = isDark ? 'alidade_smooth_dark' : 'alidade_smooth';

        if (this.currentTileLayer) {
            this.map.removeLayer(this.currentTileLayer);
        }

        this.currentTileLayer = this.L.tileLayer(
            'https://tiles.stadiamaps.com/tiles/' + themeMap + '/{z}/{x}/{y}{r}.png',
            {
                attribution: '&copy; Stadia Maps, &copy; OpenStreetMap contributors'
            }
        ).addTo(this.map);

        this.deleteMarker();
    }

    private deleteMarker() {

        this.markers.forEach(m => m.remove());
        this.markers = [];
    }

    resetNotif() {
        this.not.reset(this, this.cdr);
    }
}