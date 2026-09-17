import { Component, EventEmitter, Output, Input, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';

interface NavItem {
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
export class SidebarComponent implements OnInit, OnDestroy {
  @Input() isCollapsed = false;
  @Output() collapseChange = new EventEmitter<boolean>();
  menuItems: NavItem[] = [];
  role: string | null = null;
  username: string = '';
  orgName: string = '';
  private routerSub?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.refreshMenu();

    this.routerSub = this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.refreshMenu();
      }
    });
  }

  ngOnDestroy(): void {
    if (this.routerSub) {
      this.routerSub.unsubscribe();
    }
  }

  refreshMenu(): void {
    this.role = this.authService.getUserRole();
    const decoded = this.authService.getDecodedToken();
    this.username = decoded?.username || '';
    this.orgName = this.authService.getOrganizationName() || localStorage.getItem('OrgName') || '';

    this.menuItems = this.getMenuItemsForRole(this.role);
  }

  getMenuItemsForRole(role: string | null): NavItem[] {
    if (role === 'Admin') {
      return [
        { label: 'Dashboard', route: '/admin-dashboard', icon: 'dashboard', exact: true },
        { label: 'Notifications Center', route: '/admin-dashboard/notifications', icon: 'notifications_active' },
        { label: 'Appointments', route: '/admin-dashboard/appointments', icon: 'event' },
        { label: 'Organizations', route: '/admin-dashboard/organizations', icon: 'business' },
        { label: 'Subscriptions', route: '/admin-dashboard/subscriptions', icon: 'credit_card' },
        { label: 'Transactions', route: '/admin-dashboard/transactions', icon: 'payments' },
        { label: 'Platform & Gateway Setup', route: '/admin-dashboard/platform', icon: 'tune' },
        { label: 'Audit & Security Logs', route: '/admin-dashboard/audit-logs', icon: 'verified_user' },
        { label: 'Analytics & Reports', route: '/admin-dashboard/reports', icon: 'insights' }
      ];
    } else if (role === 'Organization' || role === 'Manager') {
      return [
        { label: 'Overview', route: '/org-dashboard', icon: 'dashboard', exact: true },
        { label: 'Notifications', route: '/org-dashboard/notifications', icon: 'notifications_active' },
        { label: 'Bookings & Schedule', route: '/org-dashboard/bookings', icon: 'calendar_month' },
        { label: 'Customer CRM', route: '/org-dashboard/customers', icon: 'people' },
        { label: 'Services Catalog', route: '/org-dashboard/services', icon: 'medical_services' },
        { label: 'WhatsApp & Meta Bot', route: '/org-dashboard/whatsapp', icon: 'chat' },
        { label: 'Team & Staff', route: '/org-dashboard/staff', icon: 'badge' },
        { label: 'Billing & Invoices', route: '/org-dashboard/transactions', icon: 'receipt_long' },
        { label: 'Platform Workspace', route: '/org-dashboard/workspace', icon: 'auto_fix_high' },
        { label: 'Branches', route: '/org-dashboard/branches', icon: 'store' },
        { label: 'Organization Profile', route: '/org-dashboard/profile', icon: 'domain' },
        { label: 'Plan & Billing', route: '/org-dashboard/subscription', icon: 'workspace_premium' }
      ];
    } else if (role === 'Staff') {
      return [
        { label: 'Staff Dashboard', route: '/org-dashboard', icon: 'dashboard', exact: true },
        { label: 'Duty Notifications', route: '/org-dashboard/notifications', icon: 'notifications_active' },
        { label: 'Schedule & Bookings', route: '/org-dashboard/bookings', icon: 'event_available' },
        { label: 'Customer Directory', route: '/org-dashboard/customers', icon: 'people' },
        { label: 'WhatsApp Messenger', route: '/org-dashboard/whatsapp', icon: 'chat' },
        { label: 'Profile & Settings', route: '/org-dashboard/profile', icon: 'person' }
      ];
    } else {
      return [];
    }
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.collapseChange.emit(this.isCollapsed);
  }

  getRoleBadgeLabel(): string {
    if (this.role === 'Admin') return 'Super Admin';
    if (this.role === 'Organization') return 'Clinic Admin';
    if (this.role === 'Staff') return 'Staff Member';
    return this.role || 'User';
  }
}
