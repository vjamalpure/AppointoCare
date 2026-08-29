import { Component, OnInit } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'appointocore-frontend';
  isSidebarCollapsed = true;
  username: string = '';
  organizationName: string = '';
  showLayout = true;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    // ✅ Hide toolbar/sidebar on login page and refresh user info on navigation
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.showLayout = !event.url.includes('/login');
        if (this.authService.isLoggedIn()) {
          const decoded = this.authService.getDecodedToken();
          this.username = decoded?.username ?? '';
          this.organizationName = localStorage.getItem("OrgName") ?? sessionStorage.getItem("OrgName") ?? "";
        } else {
          this.username = '';
          this.organizationName = '';
        }
      }
    });
  }

  toggleSidebar(): void {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  onSidebarCollapse(isCollapsed: boolean): void {
    this.isSidebarCollapsed = isCollapsed;
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  getSidebarClass(): string {
    return this.isSidebarCollapsed ? 'collapsed' : '';
  }

  getMainContentClass(): string {
    return this.isSidebarCollapsed ? 'collapsed' : '';
  }
}
