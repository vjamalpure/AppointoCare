import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMonthlyTransactionSummary(year?: number): Observable<any[]> {
    const url = `${this.apiUrl}/admin/transactions/summary${year ? '?year=' + year : ''}`;
    return this.http.get<any[]>(url);
  }

  getOrganizations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/organizations`);
  }

  createOrganization(body: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/organization/create`, body);
  }

  updateOrganization(orgId: number, body: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/admin/organization/${orgId}/update`, body);
  }

  deleteOrganization(orgId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/organization/${orgId}/delete`);
  }

  getOrganizationUsers(orgId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/organization/${orgId}/users`);
  }

  createOrganizationUser(orgId: number, body: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/organization/${orgId}/user/create`, body);
  }

  updateOrganizationUser(orgId: number, userId: number, body: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/admin/organization/${orgId}/user/${userId}/update`, body);
  }

  deleteOrganizationUser(orgId: number, userId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/organization/${orgId}/user/${userId}/delete`);
  }

  getSubscriptions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/subscriptions`);
  }

  getTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/transactions`);
  }

  getAppointments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/appointments`);
  }

  updateAppointment(id: number, body: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/appointments/${id}`, body);
  }

  deleteAppointment(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/appointments/${id}`);
  }

  getDashboardSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/admin/dashboard`);
  }

  getReportsSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/v1/platform/reports/summary`);
  }

  updateOrganizationSettings(orgId: number, settings: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/admin/organization/${orgId}/settings`, settings);
  }

  toggleUserStatus(orgId: number, userId: number, isActive?: boolean): Observable<any> {
    return this.http.patch(`${this.apiUrl}/admin/organization/${orgId}/user/${userId}/toggle-status`, { is_active: isActive });
  }

  broadcastNotification(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/v1/admin/broadcast-notification`, payload);
  }

  getAnalyticsReports(sector?: string, orgId?: number): Observable<any> {
    let params: any = {};
    if (sector && sector !== 'ALL') params.sector = sector;
    if (orgId) params.organization_id = orgId;
    return this.http.get<any>(`${this.apiUrl}/api/v1/admin/analytics-reports`, { params });
  }

  getComplaints(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/v1/platform/complaints`);
  }

  resolveComplaint(id: number, body: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/api/v1/platform/complaints/${id}/resolve`, body);
  }
}
