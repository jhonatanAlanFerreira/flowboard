import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { DrawerModule } from 'primeng/drawer';

@Component({
  selector: 'app-side-menu-component',
  imports: [DrawerModule, FormsModule],
  templateUrl: './side-menu-component.html',
  styleUrl: './side-menu-component.css',
})
export class SideMenuComponent {
  constructor(private router: Router) {}

  visible = false;

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('lastUsedWorkspace');
    this.router.navigate(['/login']);
  }
}
