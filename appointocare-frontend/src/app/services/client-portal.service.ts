import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PortalCustomerOverview {
  customer: {
    id: number;
    name: string;
    email?: string;
    phone: string;
    address?: string;
  };
  organization: {
    id: number;
    name: string;
    sector: string;
  };
  communication_preferences: {
    whatsapp: boolean;
    email: boolean;
    sms?: boolean;
  };
  appointments: Array<{
    id: number;
    service_name: string;
    staff_name: string;
    appointment_date: string;
    status: string;
    payment_status: string;
  }>;
  industry_records: Array<{
    id: number;
    sector: string;
    record_type: string;
    title: string;
    status: string;
    data: any;
    created_at: string;
    appointment_id?: number;
  }>;
  documents: Array<{
    id: number;
    title: string;
    file_name: string;
    file_type: string;
    status: string;
    uploaded_by: string;
    created_at: string;
  }>;
}

@Injectable({
  providedIn: 'root'
})
export class ClientPortalService {
  private baseUrl = environment.apiUrl || 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  public requestCode(payload: { phone?: string; email?: string; organization_id?: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/portal/auth/request-code`, payload);
  }

  public verifyCode(payload: { session_token: string; auth_code: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/portal/auth/verify`, payload);
  }

  public getOverview(sessionToken: string): Observable<PortalCustomerOverview> {
    const headers = new HttpHeaders({ 'X-Portal-Token': sessionToken });
    return this.http.get<PortalCustomerOverview>(`${this.baseUrl}/api/v1/portal/overview`, { headers });
  }

  public uploadDocument(sessionToken: string, payload: { title: string; file_name: string; content?: string; record_id?: number }): Observable<any> {
    const headers = new HttpHeaders({ 'X-Portal-Token': sessionToken });
    return this.http.post<any>(`${this.baseUrl}/api/v1/portal/documents/upload`, payload, { headers });
  }

  public respondToRecord(sessionToken: string, recordId: number, payload: { decision: string; notes?: string }): Observable<any> {
    const headers = new HttpHeaders({ 'X-Portal-Token': sessionToken });
    return this.http.post<any>(`${this.baseUrl}/api/v1/portal/records/${recordId}/respond`, payload, { headers });
  }

  public getPreferences(sessionToken: string): Observable<any> {
    const headers = new HttpHeaders({ 'X-Portal-Token': sessionToken });
    return this.http.get<any>(`${this.baseUrl}/api/v1/portal/preferences`, { headers });
  }

  public updatePreferences(sessionToken: string, preferences: { whatsapp: boolean; email: boolean; sms: boolean }): Observable<any> {
    const headers = new HttpHeaders({ 'X-Portal-Token': sessionToken });
    return this.http.post<any>(`${this.baseUrl}/api/v1/portal/preferences`, preferences, { headers });
  }
}
