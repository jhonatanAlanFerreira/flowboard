import { inject } from '@angular/core';
import {
  HttpEvent,
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';
import { RequestStatusService } from './request-status.service';

export const requestStatusInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
): Observable<HttpEvent<unknown>> => {
  const requestStatusService = inject(RequestStatusService);

  if (req.headers.has('x-skip-status')) {
    return next(req);
  }

  requestStatusService.requestStarted();

  return next(req).pipe(
    catchError((err) => {
      requestStatusService.requestFailed();
      return throwError(() => err);
    }),
    finalize(() => {
      requestStatusService.requestFinished();
    }),
  );
};
