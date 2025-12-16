import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners,
  provideAppInitializer,
  inject,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { xsrfInterceptor } from './xsrf.interceptor';
import { ConfigService } from './config.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([xsrfInterceptor])),

    provideAppInitializer(() => {
      const configService = inject(ConfigService);
      return configService.load();
    }),
  ],
};
