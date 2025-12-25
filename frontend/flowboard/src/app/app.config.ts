import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners,
  provideAppInitializer,
  inject,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { ConfigService } from './config.service';
import { authInterceptor } from './auth.interceptor';
import { requestStatusInterceptor } from './request-status.interceptor';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideAppInitializer(() => {
      const configService = inject(ConfigService);
      return configService.load();
    }),
    provideHttpClient(
      withInterceptors([authInterceptor, requestStatusInterceptor]),
    ),
    providePrimeNG({
      theme: {
        preset: Aura,
      },
    }),
  ],
};
