import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subscription } from 'rxjs';
import { AuthService } from '../../auth/auth.service';
import { NotificationService, AppNotification, NotificationStats } from '../../services/notification.service';

@Component({
  selector: 'app-notifications-center',
  templateUrl: './notifications-center.component.html',
  styleUrls: ['./notifications-center.component.scss']
})
export class NotificationsCenterComponent implements OnInit, OnDestroy {
  role: string = 'Staff';
  notifications: AppNotification[] = [];
  filteredNotifications: AppNotification[] = [];
  unreadCount: number = 0;
  stats: NotificationStats = {
    total: 0,
    unread: 0,
    by_category: { booking: 0, payment: 0, organization: 0, complaint: 0, inquiry: 0, triage: 0, system: 0 }
  };

  selectedCategory: string = 'all';
  unreadOnly: boolean = false;
  searchQuery: string = '';
  includeStaffForOrg: boolean = false;
  isLoading: boolean = false;

  // Complaints & Inquiries for Super Admin view
  complaints: any[] = [];
  showTicketModal: boolean = false;
  ticketForm = {
    type: 'Complaint' as 'Complaint' | 'Inquiry',
    subject: '',
    details: '',
    organization_name: 'City Care Health & Dental',
    priority: 'High'
  };

  private subs: Subscription = new Subscription();

  constructor(
    private notificationService: NotificationService,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.role = this.authService.getUserRole() || 'Staff';
    this.loadNotifications();

    this.subs.add(
      this.notificationService.notifications$.subscribe(notifs => {
        this.notifications = notifs;
        this.applyFilter();
      })
    );

    this.subs.add(
      this.notificationService.unreadCount$.subscribe(count => {
        this.unreadCount = count;
      })
    );

    this.subs.add(
      this.notificationService.stats$.subscribe(s => {
        this.stats = s;
      })
    );

    if (this.role === 'Admin') {
      this.loadComplaints();
    }
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadNotifications(): void {
    this.isLoading = true;
    this.notificationService.fetchNotificationsForCurrentUser(
      this.selectedCategory !== 'all' ? this.selectedCategory : undefined,
      this.unreadOnly,
      this.searchQuery.trim() || undefined
    ).subscribe({
      next: (res) => {
        this.notifications = res.notifications || [];
        this.unreadCount = res.unread_count || 0;
        if (res.stats) this.stats = res.stats;
        this.applyFilter();
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  loadComplaints(): void {
    this.notificationService.getComplaints().subscribe({
      next: (data) => this.complaints = data || [],
      error: () => {}
    });
  }

  applyFilter(): void {
    let result = [...this.notifications];

    if (this.selectedCategory !== 'all') {
      result = result.filter(n => n.category.toLowerCase() === this.selectedCategory.toLowerCase());
    }

    if (this.unreadOnly) {
      result = result.filter(n => !n.is_read);
    }

    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      result = result.filter(n =>
        n.title.toLowerCase().includes(q) ||
        n.message.toLowerCase().includes(q) ||
        (n.entity_type && n.entity_type.toLowerCase().includes(q))
      );
    }

    this.filteredNotifications = result;
  }

  setCategory(cat: string): void {
    this.selectedCategory = cat;
    this.applyFilter();
  }

  toggleUnreadOnly(): void {
    this.unreadOnly = !this.unreadOnly;
    this.applyFilter();
  }

  markRead(notification: AppNotification, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.markAsRead(notification.id).subscribe({
      next: () => {
        notification.is_read = true;
        this.snackBar.open('Notification marked as read', 'Dismiss', { duration: 2000 });
      }
    });
  }

  markAllRead(): void {
    this.notificationService.markAllAsRead().subscribe({
      next: () => {
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
        this.snackBar.open('All notifications marked as read', 'Dismiss', { duration: 2500 });
      }
    });
  }

  deleteNotification(notification: AppNotification, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.notificationService.deleteNotification(notification.id).subscribe({
      next: () => {
        this.notifications = this.notifications.filter(n => n.id !== notification.id);
        this.applyFilter();
        this.snackBar.open('Notification removed', 'Dismiss', { duration: 2000 });
      }
    });
  }

  clearAllRead(): void {
    this.notificationService.clearAllRead().subscribe({
      next: () => {
        this.notifications = this.notifications.filter(n => !n.is_read);
        this.applyFilter();
        this.snackBar.open('Read notifications cleared', 'Dismiss', { duration: 2500 });
      }
    });
  }

  navigateToAction(notification: AppNotification): void {
    if (!notification.is_read) {
      this.notificationService.markAsRead(notification.id).subscribe();
    }
    if (notification.action_url) {
      this.router.navigateByUrl(notification.action_url);
    }
  }

  // Simulator
  simulate(type: string): void {
    this.isLoading = true;
    this.notificationService.simulateEvent(type, 1).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.snackBar.open(`Simulated event: ${res?.notification?.title || 'Notification generated'}`, 'View', {
          duration: 3500
        });
        this.loadNotifications();
        if (this.role === 'Admin') this.loadComplaints();
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Error simulating notification', 'Close', { duration: 2500 });
      }
    });
  }

  submitTicket(): void {
    if (!this.ticketForm.subject.trim() || !this.ticketForm.details.trim()) {
      this.snackBar.open('Please fill out both subject and details.', 'Close', { duration: 2500 });
      return;
    }

    this.notificationService.submitComplaintOrInquiry(this.ticketForm).subscribe({
      next: (ticket) => {
        this.showTicketModal = false;
        this.snackBar.open(`${this.ticketForm.type} submitted (#${ticket.ticket_number})! Dispatched to Super Admin.`, 'OK', { duration: 4000 });
        this.ticketForm.subject = '';
        this.ticketForm.details = '';
        this.loadNotifications();
        this.loadComplaints();
      }
    });
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

  getCategoryBadgeClass(category: string): string {
    switch (category) {
      case 'booking': return 'badge-booking';
      case 'payment': return 'badge-payment';
      case 'organization': return 'badge-org';
      case 'complaint': return 'badge-complaint';
      case 'inquiry': return 'badge-inquiry';
      case 'triage': return 'badge-triage';
      case 'system': return 'badge-system';
      default: return 'badge-default';
    }
  }

  getSeverityBadgeClass(severity: string): string {
    switch (severity) {
      case 'urgent': return 'severity-urgent';
      case 'warning': return 'severity-warning';
      case 'success': return 'severity-success';
      default: return 'severity-info';
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
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return 'Recent';
    }
  }

  getRoleBannerTitle(): string {
    if (this.role === 'Admin') return 'Super Admin Notification Center';
    if (this.role === 'Organization') return 'Organization Admin Notification Center';
    if (this.role === 'Staff') return 'Staff Operations Notification Center';
    return 'Notification Center';
  }

  getRoleBannerDescription(): string {
    if (this.role === 'Admin') {
      return 'Platform-wide oversight feed. Monitors cross-tenant organization changes, pending subscription due payments, escalated customer complaints, and prospective client inquiries.';
    }
    if (this.role === 'Organization') {
      return 'Practice administrative feed. Tracks live Razorpay invoice payments, practice profile/schedule changes, staff roster assignments, and WhatsApp messaging quotas.';
    }
    return 'Front-desk & clinical duty feed. Receives immediate alerts whenever bookings are added, rescheduled, or cancelled, alongside urgent AI clinical triage flags.';
  }
}
