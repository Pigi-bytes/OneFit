import { Component, AfterViewInit, ViewChild, ElementRef, PLATFORM_ID, Inject, OnDestroy } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs/operators';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { poidUpdate } from "../../poidUpdate"
import { Subscription } from 'rxjs';


Chart.register(...registerables);

@Component({
  selector: 'app-graph-poid',
  imports: [CommonModule],
  templateUrl: './graph-poid.html',
  styleUrl: './graph-poid.css',
})
export class GraphPoid implements AfterViewInit, OnDestroy {

  chart!: Chart;
  private subscription?: Subscription;


  poid: any[] = [];
  dates: string[] = [];
  weights: number[] = [];
  notes: (number | 'nan')[] = [];


  constructor(private http: HttpClient, @Inject(PLATFORM_ID) private platformId: Object, private ser: poidUpdate) { }
  @ViewChild('myChart', { static: false }) myChart!: ElementRef<HTMLCanvasElement>;

  ngOnInit() {
    this.subscription = this.ser.refreshGraph$.subscribe(() => {
      this.getInformation();
    });
  }



  public getInformation() {
    this.http.get<any>('http://127.0.0.1:5000/user/getAllPoids').pipe(take(1)).subscribe(res => {

      this.poid = res.historique;

      this.dates = this.poid.map(item => item.date);
      this.weights = this.poid.map(item => item.poids);
      this.notes = this.poid.map(item => item.note);

      if (this.chart) {
        this.chart.destroy();
      }

      this.chart = new Chart(this.myChart.nativeElement, {
        type: 'line',
        data: {
          labels: this.dates,
          datasets: [
            {
              label: 'Poids',
              data: this.weights,
              backgroundColor: '#676767',
              borderColor: '#333',
              fill: false,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const note = this.notes[ctx.dataIndex];
                  if (note !== 'nan') {
                    return [
                      `Poids: ${ctx.raw}`,
                      `Note: ${note}`
                    ];
                  }
                  return `Poids: ${ctx.raw}`;
                }
              }
            }
          }
        }
      });



    });
  }
  ngOnDestroy() {
    this.subscription?.unsubscribe();
    if (this.chart) {
      this.chart.destroy();
    }
  }




  ngAfterViewInit(): void {

    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    this.getInformation();
  }

}
