import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable, interval, of } from 'rxjs';
import { catchError, switchMap, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { AuthService } from '../auth/auth.service';

export interface AppNotification {
  id: number;
  target_level: 'staff' | 'org_admin' | 'superadmin' | 'all';
  organization_id?: number | null;
  title: string;
  message: string;
  category: 'booking' | 'payment' | 'organization' | 'complaint' | 'inquiry' | 'system' | 'triage';
  severity: 'info' | 'success' | 'warning' | 'urgent';
  entity_type?: string;
  entity_id?: number;
  metadata?: any;
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

export interface NotificationStats {
  total: number;
  unread: number;
  by_category: {
    booking: number;
    payment: number;
    organization: number;
    complaint: number;
    inquiry: number;
    triage: number;
    system: number;
  };
}

export interface NotificationResponse {
  notifications: AppNotification[];
  unread_count: number;
  role: string;
  stats: NotificationStats;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly baseUrl = environment.apiUrl;

  private notificationsSubject = new BehaviorSubject<AppNotification[]>([]);
  public notifications$ = this.notificationsSubject.asObservable();

  private unreadCountSubject = new BehaviorSubject<number>(0);
  public unreadCount$ = this.unreadCountSubject.asObservable();

  private statsSubject = new BehaviorSubject<NotificationStats>({
    total: 0,
    unread: 0,
    by_category: { booking: 0, payment: 0, organization: 0, complaint: 0, inquiry: 0, triage: 0, system: 0 }
  });
  public stats$ = this.statsSubject.asObservable();

  constructor(private http: HttpClient, private authService: AuthService) {
    // Initial fetch
    this.refreshNotifications();

    // Poll periodically (every 15 seconds) to fetch fresh role-scoped notifications
    interval(15000).pipe(
      switchMap(() => this.fetchNotificationsForCurrentUser())
    ).subscribe();
  }

  fetchNotificationsForCurrentUser(category?: string, unreadOnly?: boolean, search?: string): Observable<NotificationResponse> {
    const role = this.authService.getUserRole() || 'Staff';
    let params = new HttpParams().set('role', role);

    if (category && category !== 'all') {
      params = params.set('category', category);
    }
    if (unreadOnly) {
      params = params.set('unread_only', 'true');
    }
    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<NotificationResponse>(`${this.baseUrl}/api/v1/notifications`, { params }).pipe(
      tap(res => {
        this.notificationsSubject.next(res.notifications || []);
        this.unreadCountSubject.next(res.unread_count || 0);
        if (res.stats) {
          this.statsSubject.next(res.stats);
        }
      }),
      catchError(err => {
        console.warn('Error fetching notifications:', err);
        return of({
          notifications: [],
          unread_count: 0,
          role,
          stats: { total: 0, unread: 0, by_category: { booking: 0, payment: 0, organization: 0, complaint: 0, inquiry: 0, triage: 0, system: 0 } }
        });
      })
    );
  }

  refreshNotifications(): void {
    this.fetchNotificationsForCurrentUser().subscribe();
  }

  markAsRead(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/v1/notifications/${id}/read`, {}).pipe(
      tap(() => {
        const current = this.notificationsSubject.value;
        const updated = current.map(n => n.id === id ? { ...n, is_read: true } : n);
        this.notificationsSubject.next(updated);
        const unread = updated.filter(n => !n.is_read).length;
        this.unreadCountSubject.next(unread);
      })
    );
  }

  markAllAsRead(): Observable<any> {
    const role = this.authService.getUserRole() || 'Staff';
    return this.http.post(`${this.baseUrl}/api/v1/notifications/mark-all-read`, { role }).pipe(
      tap(() => {
        const current = this.notificationsSubject.value;
        const updated = current.map(n => ({ ...n, is_read: true }));
        this.notificationsSubject.next(updated);
        this.unreadCountSubject.next(0);
      })
    );
  }

  deleteNotification(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/api/v1/notifications/${id}`).pipe(
      tap(() => {
        const current = this.notificationsSubject.value;
        const updated = current.filter(n => n.id !== id);
        this.notificationsSubject.next(updated);
        const unread = updated.filter(n => !n.is_read).length;
        this.unreadCountSubject.next(unread);
      })
    );
  }

  clearAllRead(): Observable<any> {
    const role = this.authService.getUserRole() || 'Staff';
    return this.http.delete(`${this.baseUrl}/api/v1/notifications/clear-all`, { params: { role } }).pipe(
      tap(() => {
        const current = this.notificationsSubject.value;
        const updated = current.filter(n => !n.is_read);
        this.notificationsSubject.next(updated);
      })
    );
  }

  simulateEvent(type: string, organizationId: number = 1): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/v1/notifications/simulate`, { type, organization_id: organizationId }).pipe(
      tap(() => this.refreshNotifications())
    );
  }

  // Complaints & Inquiries
  getComplaints(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/platform/complaints`);
  }

  submitComplaintOrInquiry(payload: {
    type: 'Complaint' | 'Inquiry';
    subject: string;
    details: string;
    organization_name?: string;
    priority?: string;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/v1/platform/complaints`, payload).pipe(
      tap(() => this.refreshNotifications())
    );
  }
}
