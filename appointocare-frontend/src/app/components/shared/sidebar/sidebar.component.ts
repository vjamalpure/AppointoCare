
import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';

export interface MenuItem {
  label: string;
  route: string;
  icon: string;
  exact?: boolean;
}

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  @Input() isCollapsed = false;
  @Output() collapseChange = new EventEmitter<boolean>();

  menuItems: MenuItem[] = [];
  role: string | null = null;
  orgName: string = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.refreshMenu();
  }

  refreshMenu(): void {
    this.role = this.authService.getUserRole();
    const decoded = this.authService.getDecodedToken();
    this.orgName = decoded?.organization_name || localStorage.getItem('OrgName') || '';
    this.menuItems = this.getMenuItemsForRole(this.role);
  }

  getMenuItemsForRole(role: string | null): MenuItem[] {
    if (role === 'Admin') {
      return [
        { label: 'Dashboard', route: '/admin', icon: 'dashboard', exact: true },
        { label: 'Organizations', route: '/admin/organizations', icon: 'corporate_fare' },
        { label: 'Subscriptions', route: '/admin/subscriptions', icon: 'card_membership' },
        { label: 'Transactions', route: '/admin/transactions', icon: 'receipt_long' },
        { label: 'Platform Config', route: '/admin/platform', icon: 'tune' }
      ];
    } else if (role === 'Organization' || role === 'Manager' || role === 'Staff') {
      return [
        { label: 'Dashboard', route: '/org-dashboard', icon: 'dashboard', exact: true },
        { label: 'Appointments', route: '/org-dashboard/bookings', icon: 'event_available' },
        { label: 'Transactions', route: '/org-dashboard/transactions', icon: 'receipt_long' },
        { label: 'Workspace', route: '/org-dashboard/workspace', icon: 'view_kanban' },
        { label: 'Organization Profile', route: '/org-dashboard/profile', icon: 'badge' },
        { label: 'Subscription & Plans', route: '/org-dashboard/subscription', icon: 'stars' }
      ];
    }
    return [];
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.collapseChange.emit(this.isCollapsed);
  }
}
