import { Component, OnInit } from '@angular/core';
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
  userRole: string = '';
  organizationName: string = '';
  showLayout = false;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.checkAuthState();

    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.checkAuthState(event.urlAfterRedirects || event.url);
      }
    });
  }

  private checkAuthState(currentUrl?: string): void {
    const url = currentUrl || this.router.url;
    const isAuthPage = url.includes('/login') ||
                       url.includes('/forgot-password') ||
                       url.includes('/reset-password') ||
                       url === '/';

    const loggedIn = this.authService.isLoggedIn();
    this.showLayout = !isAuthPage && loggedIn;

    if (loggedIn) {
      const decoded = this.authService.getDecodedToken();
      this.username = decoded?.username ?? '';
      this.userRole = decoded?.role ?? '';
      this.organizationName = localStorage.getItem('OrgName') ?? sessionStorage.getItem('OrgName') ?? decoded?.organization_name ?? '';
    } else {
      this.username = '';
      this.userRole = '';
      this.organizationName = '';
    }
  }

  toggleSidebar(): void {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  onSidebarCollapse(isCollapsed: boolean): void {
    this.isSidebarCollapsed = isCollapsed;
  }
}
