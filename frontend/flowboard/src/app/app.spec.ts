import { ComponentFixture, TestBed } from '@angular/core/testing';
import { App } from './app';
import { MessageService } from 'primeng/api';
import { provideRouter } from '@angular/router';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('App', () => {
  let component: App;
  let fixture: ComponentFixture<App>;
  let messageService: MessageService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), MessageService],
    }).compileComponents();

    fixture = TestBed.createComponent(App);
    component = fixture.componentInstance;

    messageService = fixture.debugElement.injector.get(MessageService);

    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should have a toast component in the view', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('p-toast')).not.toBeNull();
  });

  it('should provide the MessageService', () => {
    expect(messageService).toBeDefined();
    expect(typeof messageService.add).toBe('function');
  });
});
