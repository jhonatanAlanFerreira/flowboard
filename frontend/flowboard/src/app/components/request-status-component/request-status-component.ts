import { Component } from '@angular/core';
import { RequestStatusService } from '../../request-status.service';

@Component({
  selector: 'app-request-status-component',
  imports: [],
  templateUrl: './request-status-component.html',
  styleUrl: './request-status-component.css',
})
export class RequestStatusComponent {
  constructor(public requestStatusService: RequestStatusService) {}
}
