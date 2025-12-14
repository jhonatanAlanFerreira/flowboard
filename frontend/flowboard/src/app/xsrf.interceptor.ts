import { HttpEvent, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Observable, from, switchMap } from 'rxjs';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

let csrfInitialized = false;

export const xsrfInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const http = inject(HttpClient);

  req = req.clone({ withCredentials: true });

  const xsrfToken = getXsrfToken();

  if (xsrfToken || csrfInitialized || req.url.includes('/sanctum/csrf-cookie')) {
    return next(addXsrfHeader(req, xsrfToken));
  }

  csrfInitialized = true;

  return from(
    http.get('http://localhost:8001/sanctum/csrf-cookie', {
      withCredentials: true,
    })
  ).pipe(
    switchMap(() => {
      const token = getXsrfToken();
      return next(addXsrfHeader(req, token));
    })
  );
};

function getXsrfToken(): string | null {
  const match = document.cookie.match(/XSRF-TOKEN=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

function addXsrfHeader(req: HttpRequest<any>, token: string | null) {
  if (!token) return req;

  return req.clone({
    setHeaders: {
      'X-XSRF-TOKEN': token,
    },
  });
}
