import { Injectable, signal, computed } from '@angular/core';

type RequestUiState = 'idle' | 'loading' | 'success' | 'error';

@Injectable({ providedIn: 'root' })
export class RequestStatusService {
  private activeRequests = signal(0);
  private hasErrorInternal = signal(false);
  private showSuccess = signal(false);

  readonly state = computed<RequestUiState>(() => {
    if (this.hasErrorInternal()) return 'error';
    if (this.activeRequests() > 0) return 'loading';
    if (this.showSuccess()) return 'success';
    return 'idle';
  });

  requestStarted() {
    this.activeRequests.update((v) => v + 1);
  }

  requestFinished() {
    this.activeRequests.update((v) => Math.max(0, v - 1));

    if (this.activeRequests() === 0 && !this.hasErrorInternal()) {
      this.triggerSuccess();
    }
  }

  requestFailed() {
    this.hasErrorInternal.set(true);
  }

  private triggerSuccess() {
    this.showSuccess.set(true);

    setTimeout(() => {
      this.showSuccess.set(false);
    }, 2000);
  }
}
