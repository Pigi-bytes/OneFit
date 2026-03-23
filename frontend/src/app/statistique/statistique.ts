import { Component, ViewChild, ElementRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Erreur } from '../erreur';
import { ChangeDetectorRef } from '@angular/core';
import { Chart, registerables, ChartConfiguration } from 'chart.js';
import { Theme } from '../theme';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-statistique',
    imports: [FormsModule, CommonModule],
    templateUrl: './statistique.html',
    styleUrl: './statistique.css',
})
export class Statistique {
    private themeSubscription?: Subscription;

    exoChoisit: string = '';
    exercices: any[] = [];
    backendResponse = "";
    chart!: Chart<'line'>;
    stat: any[] = [];

    constructor(private http: HttpClient, private erreur: Erreur, private cdr: ChangeDetectorRef, private theme: Theme) { Chart.register(...registerables); }
    @ViewChild('myChart', { static: false }) myChart!: ElementRef<HTMLCanvasElement>;



    ngOnInit() {
        this.themeSubscription = this.theme.themeChange$.subscribe(() => {
            this.updateChartColors();
        });

        this.http.get('http://127.0.0.1:5000/user/getLoggedExercises', {}).subscribe({

            next: (res: any) => {
                console.log('RESPONSE OK', res);
                this.exercices = res['exercises'];
                this.backendResponse = res.message;
                this.cdr.detectChanges();
            },

            error: (err: any) => { this.backendResponse = this.erreur.erreur(err); this.cdr.detectChanges(); }
        });


    }

    public getInformation() {
        const isDark = localStorage.getItem('darkMode') === 'true';
        console.log(this.exoChoisit);

        this.http.post('http://127.0.0.1:5000/user/getExoStat', {
            exoId: this.exoChoisit
        }).subscribe({

            next: (res: any) => {
                this.stat = res.stats;


                if (this.chart) {
                    this.chart.destroy();
                }

                const config: ChartConfiguration<'line'> = {
                    type: 'line',
                    data: {
                        labels: this.stat.map(s => s.day),
                        datasets: [
                            {
                                label: 'Volume',
                                data: this.stat.map(s => s.volume),
                                backgroundColor: '#676767',
                                borderColor: isDark ? '#4ade80' : '#2563eb',
                                pointBackgroundColor: isDark ? '#ffffff' : '#333333',
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
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: {
                                    color: isDark
                                        ? 'rgba(255,255,255,0.15)'
                                        : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: isDark ? '#ffffff' : '#333333'
                                }
                            },
                            y: {
                                grid: {
                                    color: isDark
                                        ? 'rgba(255,255,255,0.15)'
                                        : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: isDark ? '#ffffff' : '#333333'
                                }
                            }
                        }
                    }
                };

                this.chart = new Chart(this.myChart.nativeElement, config);


            }
        });
    }

    private updateChartColors() {
        if (!this.chart) return;

        const isDark = this.theme.isItDark();

        this.chart.data.datasets[0].borderColor = isDark ? '#4ade80' : '#2563eb';
        this.chart.data.datasets[0].pointBackgroundColor = isDark ? '#ffffff' : '#333333';

        if (this.chart.options.scales) {
            if (this.chart.options.scales['x']) {
                this.chart.options.scales['x'].grid = {
                    color: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)'
                };
                this.chart.options.scales['x'].ticks = {
                    color: isDark ? '#ffffff' : '#333333'
                };
            }
            if (this.chart.options.scales['y']) {
                this.chart.options.scales['y'].grid = {
                    color: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)'
                };
                this.chart.options.scales['y'].ticks = {
                    color: isDark ? '#ffffff' : '#333333'
                };
            }
        }

        this.chart.update();
    }



}
