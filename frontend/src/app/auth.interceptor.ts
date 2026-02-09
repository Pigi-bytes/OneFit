import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
        if (typeof localStorage !== 'undefined') {
                const token = localStorage.getItem('access_token');

                if (token) {
                        const clonedRequest = req.clone({
                                setHeaders: {
                                        Authorization: `Bearer ${token}`
                                }
                        });
                        return next(clonedRequest);
                }
        }

        return next(req);
};