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
}
