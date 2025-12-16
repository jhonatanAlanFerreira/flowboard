import {
  HttpEvent,
  HttpHandlerFn,
  HttpInterceptorFn,
  HttpRequest,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, from, switchMap, catchError, throwError } from 'rxjs';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { ConfigService } from './config.service';

let csrfInitialized = false;

export const xsrfInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const http = inject(HttpClient);
  const router = inject(Router);
  const config = inject(ConfigService);

  req = req.clone({ withCredentials: true });

  const xsrfToken = getXsrfToken();

  const handleRequest = (request: HttpRequest<unknown>) =>
    next(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          if (!router.url.startsWith('/login')) {
            router.navigate(['/login']);
          }
        }

        return throwError(() => error);
      })
    );

  if (xsrfToken || csrfInitialized || req.url.includes('/sanctum/csrf-cookie')) {
    return handleRequest(addXsrfHeader(req, xsrfToken));
  }

  csrfInitialized = true;

  return from(
    http.get(`${config.apiBaseUrl}/sanctum/csrf-cookie`, {
      withCredentials: true,
    })
  ).pipe(
    switchMap(() => {
      const token = getXsrfToken();
      return handleRequest(addXsrfHeader(req, token));
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
