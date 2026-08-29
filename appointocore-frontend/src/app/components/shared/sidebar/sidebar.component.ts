
import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  @Output() collapseChange = new EventEmitter<boolean>();
  isCollapsed = true;
  menuItems: any[] = [];
  role: string | null = null;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.role = this.authService.getUserRole();
    this.menuItems = this.getMenuItemsForRole(this.role);
    // Auto collapse after 2 seconds
    setTimeout(() => {
      this.isCollapsed = true;
      this.collapseChange.emit(this.isCollapsed);
    }, 2000);
  }

  getMenuItemsForRole(role: string | null) {
    if (role === 'Admin') {
      return [
        { label: 'Dashboard', route: '/admin-dashboard', icon: '🏠' },
        { label: 'Organizations', route: '/admin/organizations', icon: '🏢' },
        { label: 'Subscriptions', route: '/admin/subscriptions', icon: '💳' },
        { label: 'Transactions', route: '/admin/transactions', icon: '💰' },
      ];
    } else if (role === 'Organization') {
      return [
        { label: 'Dashboard', route: '/org-dashboard', icon: '🏠' },
        { label: 'Bookings', route: '/org-dashboard/bookings', icon: '📅' },
        { label: 'Transactions', route: '/org-dashboard/transactions', icon: '💰' },
        { label: 'Profile', route: '/org-dashboard/profile', icon: '👤' },
        { label: 'Subscription', route: '/org-dashboard/subscription', icon: '💳' },
        // Add more as needed
      ];
    } else {
      return [];
    }
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.collapseChange.emit(this.isCollapsed);
  }
}
