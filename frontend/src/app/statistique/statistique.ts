import { Component, ViewChild, ElementRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Erreur } from '../erreur';
import { ChangeDetectorRef } from '@angular/core';
import { Chart, registerables, ChartConfiguration } from 'chart.js';
import { Theme } from '../theme';
import { ignoreElements, Subscription } from 'rxjs';

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
    description = "";
    isDark: boolean = false;

    titreGraphe = "Sélectionnez un graphe à afficher";

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

    public getInformation(typeGraphe: any) {
        console.log(this.exoChoisit);


        if (this.exoChoisit === "") {
            return;
        }

        switch (typeGraphe) {
            case 1: this.titreGraphe = "Volume";
                this.description = "Le volume total de poids soulevé lors d’une séance de musculation est un indicateur qui permet de mesurer la quantité de travail effectuée. Il correspond à la somme de toutes les charges déplacées pendant l’entraînement. Pour le calculer, on utilise la formule suivante : volume = séries × répétitions × charge (en kilogrammes). Il suffit donc de multiplier, pour chaque exercice, le nombre de séries par le nombre de répétitions et par la charge utilisée, puis d’additionner les résultats de tous les exercices afin d’obtenir le volume total de la séance."; break;
            case 2: this.titreGraphe = "1 RM";
                this.description = "Le 1RM(une répétition maximale) correspond au poids maximal qu’une personne peut soulever une seule fois sur un exercice donné. Comme il est difficile à mesurer directement, il est souvent estimé à partir des performances réalisées avec des charges plus légères. Une formule courante consiste à utiliser le nombre de répétitions et la charge soulevée pour obtenir une estimation du 1RM. Cela permet de suivre sa progression en force sans avoir à tester systématiquement sa charge maximale."; break;
            case 3:
                this.titreGraphe = "Poids max";
                this.description = "Le poids maximal correspond à la charge la plus lourde soulevée lors d’une séance pour un exercice donné. Contrairement au 1RM estimé, il s’agit d’une valeur réelle observée pendant l’entraînement. Pour le déterminer, il suffit d’identifier la répétition où la charge utilisée est la plus élevée. Cet indicateur permet de suivre l’évolution de la force maximale au fil du temps.";
                break;
        }

        this.cdr.detectChanges();

        this.http.post('http://127.0.0.1:5000/user/getExoStat', {
            exoId: this.exoChoisit
        }).subscribe({

            next: (res: any) => {
                this.stat = res.stats;


                if (this.chart) {
                    this.chart.destroy();
                }
                const isDark = this.theme.isItDark();

                console.log(isDark);

                const config: ChartConfiguration<'line'> = {
                    type: 'line',
                    data: {
                        labels: this.stat.map(s => s.day),
                        datasets: [
                            {
                                label: typeGraphe === 1
                                    ? 'Volume'
                                    : typeGraphe === 2
                                        ? '1RM estimé'
                                        : 'Poids max',
                                data: this.stat.map(s => {
                                    if (typeGraphe === 1)
                                        return s.volume
                                    else if (typeGraphe === 2)
                                        return s.estimated_1rm
                                    else
                                        return s.max_weight
                                }),
                                backgroundColor: '#676767',
                                borderColor: this.isDark ? '#4ade80' : '#2563eb',
                                pointBackgroundColor: this.isDark ? '#ffffff' : '#333333',
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
                                    color: this.isDark
                                        ? 'rgba(255,255,255,0.15)'
                                        : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: this.isDark ? '#ffffff' : '#333333'
                                }
                            },
                            y: {
                                grid: {
                                    color: this.isDark
                                        ? 'rgba(255,255,255,0.15)'
                                        : 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    color: this.isDark ? '#ffffff' : '#333333'
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

        this.isDark = this.theme.isItDark();

        this.chart.data.datasets[0].borderColor = this.isDark ? '#4ade80' : '#2563eb';
        this.chart.data.datasets[0].pointBackgroundColor = this.isDark ? '#ffffff' : '#333333';

        if (this.chart.options.scales) {
            if (this.chart.options.scales['x']) {
                this.chart.options.scales['x'].grid = {
                    color: this.isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)'
                };
                this.chart.options.scales['x'].ticks = {
                    color: this.isDark ? '#ffffff' : '#333333'
                };
            }
            if (this.chart.options.scales['y']) {
                this.chart.options.scales['y'].grid = {
                    color: this.isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)'
                };
                this.chart.options.scales['y'].ticks = {
                    color: this.isDark ? '#ffffff' : '#333333'
                };
            }
        }

        this.chart.update();
    }



}
