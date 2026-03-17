import { ChangeDetectorRef, Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class Erreur {

    public erreur(err: any) {
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

            return messages.join('\n');
        }
        // erreurs HTTP (400, 409, 500...)
        else if (err.error && err.error.message) {
            return err.error.message;
        } else {
            return 'Erreur serveur';
        }

    }

}
