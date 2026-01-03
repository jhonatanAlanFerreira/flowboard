import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Divider } from 'primeng/divider';
import { DrawerModule } from 'primeng/drawer';
import { LoginService } from '../../../../services/login/login-service';

@Component({
  selector: 'app-side-menu-component',
  imports: [DrawerModule, FormsModule, Divider],
  templateUrl: './side-menu-component.html',
  styleUrl: './side-menu-component.css',
})
export class SideMenuComponent {
  @Output() onCreateWorkspace = new EventEmitter();
  @Output() onAiCreateWorkspace = new EventEmitter();

  visible = false;

  constructor(
    private router: Router,
    private loginService: LoginService,
  ) {}

  logout() {
    this.loginService.logout();
    this.router.navigate(['/login']);
  }

  createWorkspace() {
    this.visible = false;
    this.onCreateWorkspace.emit();
  }

  createWorkspaceWithAi() {
    this.visible = false;
    this.onAiCreateWorkspace.emit();
  }
}
