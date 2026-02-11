import { Component, AfterViewInit, ViewChild, ElementRef, PLATFORM_ID, Inject } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { isPlatformBrowser } from '@angular/common';

Chart.register(...registerables);

@Component({
  selector: 'app-graph-poid',
  imports: [],
  templateUrl: './graph-poid.html',
  styleUrl: './graph-poid.css',
})
export class GraphPoid implements AfterViewInit {

  @ViewChild('myChart', { static: false }) myChart!: ElementRef<HTMLCanvasElement>;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) { }

  chart!: Chart;

  config = {
    type: 'bar',
    data: {
      labels: ['JAN', 'FEB', 'MAR', 'APR'],
      datasets: [
        {
          label: 'Sales',
          data: [467, 576, 572, 588],
          backgroundColor: '#676767',
        },
        {
          label: 'PAT',
          data: [100, 120, 123, 134],
          backgroundColor: 'red',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  };

  ngAfterViewInit(): void {

    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    if (!this.myChart) {
      console.error('Canvas introuvable');
      return;
    }

    this.chart = new Chart(this.myChart.nativeElement, this.config as any);
  }

}
