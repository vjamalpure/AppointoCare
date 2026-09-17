import { Component, EventEmitter, Output, Input, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { IndustryService } from '../../../services/industry.service';
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
  sector: string = 'Healthcare';
  private routerSub?: Subscription;

  constructor(
    private authService: AuthService,
    private industry: IndustryService,
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
    this.sector = this.authService.getSector();
    this.industry.setSector(this.sector, false);

    this.menuItems = this.getMenuItemsForRole(this.role);
  }

  getMenuItemsForRole(role: string | null): NavItem[] {
    const terms = this.industry.getTerms(this.sector);

    if (role === 'Admin' || role === 'SuperAdmin') {
      return [
        { label: 'Platform Overview', route: '/admin-dashboard', icon: 'dashboard', exact: true },
        { label: 'Notifications Center', route: '/admin-dashboard/notifications', icon: 'notifications_active' },
        { label: 'Global Appointments', route: '/admin-dashboard/appointments', icon: 'event' },
        { label: 'Tenants & Organizations', route: '/admin-dashboard/organizations', icon: 'business' },
        { label: 'Subscriptions & Tiers', route: '/admin-dashboard/subscriptions', icon: 'credit_card' },
        { label: 'Platform Transactions', route: '/admin-dashboard/transactions', icon: 'payments' },
        { label: 'Platform Configuration', route: '/admin-dashboard/platform', icon: 'tune' },
        { label: 'Security & Audit Logs', route: '/admin-dashboard/audit-logs', icon: 'verified_user' },
        { label: 'Analytics & Reports', route: '/admin-dashboard/reports', icon: 'insights' }
      ];
    } else if (role === 'Organization' || role === 'Manager') {
      return [
        { label: 'Overview', route: '/org-dashboard', icon: 'dashboard', exact: true },
        { label: 'Notifications', route: '/org-dashboard/notifications', icon: 'notifications_active' },
        { label: `${terms.appointmentPluralLabel} & Schedule`, route: '/org-dashboard/bookings', icon: 'calendar_month' },
        { label: `${this.sector} Suite & Add-ons`, route: '/org-dashboard/industry-suite', icon: 'extension' },
        { label: `${terms.customerPluralLabel} CRM`, route: '/org-dashboard/customers', icon: 'people' },
        { label: `${terms.servicePluralLabel} Catalog`, route: '/org-dashboard/services', icon: 'medical_services' },
        { label: 'WhatsApp & Reception Bot', route: '/org-dashboard/whatsapp', icon: 'chat' },
        { label: `${terms.staffPluralLabel}`, route: '/org-dashboard/staff', icon: 'badge' },
        { label: 'Billing & Invoices', route: '/org-dashboard/transactions', icon: 'receipt_long' },
        { label: 'Platform Workspace', route: '/org-dashboard/workspace', icon: 'auto_fix_high' },
        { label: `${terms.branchPluralLabel}`, route: '/org-dashboard/branches', icon: 'store' },
        { label: 'Organization Profile', route: '/org-dashboard/profile', icon: 'domain' },
        { label: 'Plan & Subscription', route: '/org-dashboard/subscription', icon: 'workspace_premium' }
      ];
    } else {
      // Specialized Staff, Doctors, Stylists, Advisors, Realtors, Consultants
      return [
        { label: 'Overview', route: '/org-dashboard', icon: 'dashboard', exact: true },
        { label: 'Duty Notifications', route: '/org-dashboard/notifications', icon: 'notifications_active' },
        { label: `My ${terms.appointmentPluralLabel}`, route: '/org-dashboard/bookings', icon: 'event_available' },
        { label: `${this.sector} Tool & Records`, route: '/org-dashboard/industry-suite', icon: 'extension' },
        { label: `${terms.customerPluralLabel} Directory`, route: '/org-dashboard/customers', icon: 'people' },
        { label: `${terms.servicePluralLabel}`, route: '/org-dashboard/services', icon: 'medical_services' },
        { label: 'WhatsApp Messenger', route: '/org-dashboard/whatsapp', icon: 'chat' },
        { label: 'My Profile & Schedule', route: '/org-dashboard/profile', icon: 'person' }
      ];
    }
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.collapseChange.emit(this.isCollapsed);
  }

  getRoleBadgeLabel(): string {
    if (this.role === 'Admin' || this.role === 'SuperAdmin') return 'Super Admin';
    if (this.role === 'Organization') {
      const config = this.industry.getConfig(this.sector);
      return `${config.sector} Admin`;
    }
    return this.role || 'Staff';
  }
}
