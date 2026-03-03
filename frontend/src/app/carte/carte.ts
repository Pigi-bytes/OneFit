import { Component, AfterViewInit, Inject, PLATFORM_ID, ViewEncapsulation } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';

@Component({
  selector: 'app-carte',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './carte.html',
  styleUrl: './carte.css',
  encapsulation: ViewEncapsulation.None
})


export class Carte implements AfterViewInit {

  private map!: L.Map;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  async ngAfterViewInit(): Promise<void> {
    if (isPlatformBrowser(this.platformId)) {
      
      const L = await import('leaflet');

      const map = L.map('map').setView([47.988, 0.160], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      const triggerTabList = document.querySelectorAll('[data-bs-toggle="tab"]');

    }
  }
}