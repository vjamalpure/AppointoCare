import { Component, OnInit, HostListener } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'appointocare-frontend';
  isSidebarCollapsed = false;
  username: string = '';
  organizationName: string = '';
  showLayout = true;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.checkResolution();
    // Hide toolbar/sidebar on auth pages and refresh user info on navigation
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        const url = event.urlAfterRedirects || event.url;
        this.showLayout = !url.includes('/login') && !url.includes('/forgot-password') && !url.includes('/reset-password');
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

  @HostListener('window:resize', ['$event'])
  onResize(): void {
    this.checkResolution();
  }

  private checkResolution(): void {
    if (typeof window !== 'undefined') {
      if (window.innerWidth < 1100 && !this.isSidebarCollapsed) {
        this.isSidebarCollapsed = true;
      }
    }
  }

  getSidebarClass(): string {
    return this.isSidebarCollapsed ? 'collapsed' : '';
  }

  getMainContentClass(): string {
    return this.isSidebarCollapsed ? 'collapsed' : '';
  }
}
