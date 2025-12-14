import { HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

export const xsrfInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const match = document.cookie.match(/XSRF-TOKEN=([^;]+)/);
  const xsrfToken = match ? decodeURIComponent(match[1]) : null;

  if (xsrfToken) {
    req = req.clone({
      withCredentials: true,
      setHeaders: {
        'X-XSRF-TOKEN': xsrfToken,
      },
    });
  } else {
    req = req.clone({ withCredentials: true });
  }

  return next(req);
};
