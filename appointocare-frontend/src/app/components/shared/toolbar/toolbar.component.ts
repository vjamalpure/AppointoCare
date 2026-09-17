import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { NotificationService, AppNotification } from '../../../services/notification.service';
import { IndustryService } from '../../../services/industry.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent implements OnInit, OnDestroy {
  @Input() username: string = '';
  @Input() organizationName: string = '';
  @Output() toggleSidebar = new EventEmitter<void>();

  role: string | null = null;
  notifications: AppNotification[] = [];
  unreadCount: number = 0;
  private subs: Subscription = new Subscription();

  constructor(
    private authService: AuthService,
    private industry: IndustryService,
    private router: Router,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.role = this.authService.getUserRole();

    this.subs.add(
      this.notificationService.notifications$.subscribe(notifs => {
        this.notifications = notifs;
      })
    );

    this.subs.add(
      this.notificationService.unreadCount$.subscribe(count => {
        this.unreadCount = count;
      })
    );

    // Initial load
    this.notificationService.refreshNotifications();
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  onToggle(): void {
    this.toggleSidebar.emit();
  }

  markAsRead(notification: AppNotification, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.markAsRead(notification.id).subscribe();
  }

  markAllAsRead(event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.markAllAsRead().subscribe();
  }

  deleteNotification(notification: AppNotification, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.deleteNotification(notification.id).subscribe();
  }

  simulateEvent(type: string, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.simulateEvent(type).subscribe();
  }

  navigateToNotification(notification: AppNotification): void {
    if (!notification.is_read) {
      this.notificationService.markAsRead(notification.id).subscribe();
    }
    if (notification.action_url) {
      this.router.navigateByUrl(notification.action_url);
    } else {
      this.goToNotificationCenter();
    }
  }

  goToNotificationCenter(): void {
    if (this.role === 'Admin') {
      this.router.navigate(['/admin-dashboard/notifications']);
    } else {
      this.router.navigate(['/org-dashboard/notifications']);
    }
  }

  getRoleScopeNotice(): string {
    if (this.role === 'Admin' || this.role === 'SuperAdmin') return 'Super Admin • Org Changes, Payments & Inquiries';
    const terms = this.industry.getTerms();
    if (this.role === 'Organization') return `${terms.name} • Practice Updates`;
    return `${this.role || 'Staff'} • Schedule & Client Feed`;
  }

  getSectorBadge(): string {
    const sector = this.authService.getSector();
    const config = this.industry.getConfig(sector);
    return `${config.sector}`;
  }

  getRoleDisplayName(): string {
    if (this.role === 'Admin' || this.role === 'SuperAdmin') return 'Super Admin';
    if (this.role === 'Organization') {
      const config = this.industry.getConfig(this.authService.getSector());
      return `${config.sector} Portal`;
    }
    return `${this.role || 'Staff'} Portal`;
  }

  getCategoryIcon(category: string): string {
    switch (category) {
      case 'booking': return 'event_available';
      case 'payment': return 'payments';
      case 'organization': return 'corporate_fare';
      case 'complaint': return 'report_problem';
      case 'inquiry': return 'help_outline';
      case 'triage': return 'medical_services';
      case 'system': return 'tune';
      default: return 'notifications';
    }
  }

  formatTime(isoDate: string): string {
    if (!isoDate) return 'Recent';
    try {
      const date = new Date(isoDate);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return 'Recent';
    }
  }

  switchRole(targetRole: 'Admin' | 'Organization' | 'Staff'): void {
    if (targetRole === 'Admin') {
      this.authService.login('superadmin', 'Admin@12345').subscribe({
        next: () => {
          this.router.navigate(['/admin-dashboard']).then(() => {
            window.location.reload();
          });
        }
      });
    } else if (targetRole === 'Organization') {
      this.authService.login('org1', 'Org@12345', 'ORG1').subscribe({
        next: (res: any) => {
          this.authService.saveOrgName(res.organization_name || 'City Care Health & Dental');
          this.router.navigate(['/org-dashboard']).then(() => {
            window.location.reload();
          });
        }
      });
    } else if (targetRole === 'Staff') {
      this.authService.login('staff1', 'Staff@12345', 'ORG1').subscribe({
        next: (res: any) => {
          this.authService.saveOrgName(res.organization_name || 'City Care Health & Dental');
          this.router.navigate(['/org-dashboard']).then(() => {
            window.location.reload();
          });
        }
      });
    }
  }

  logout(): void {
    this.authService.logout();
  }
}
