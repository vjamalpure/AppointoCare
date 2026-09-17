import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AppointmentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAppointments(role?: string, filters?: { branch_id?: any, date?: string, status?: string }): Observable<any> {
    let params: any = {};
    if (role) params.role = role;
    if (filters?.branch_id && filters.branch_id !== 'ALL') params.branch_id = filters.branch_id;
    if (filters?.date && filters.date !== 'ALL') params.date = filters.date;
    if (filters?.status && filters.status !== 'ALL') params.status = filters.status;
    return this.http.get<any>(`${this.apiUrl}/appointments`, { params });
  }

  createAppointment(body: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/appointments`, body);
  }

  updateAppointment(id: number, body: any): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/appointments/${id}`, body);
  }

  deleteAppointment(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/appointments/${id}`);
  }

  replyAppointment(id: number, payload: { message: string, sender?: string, sender_role?: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/appointments/${id}/reply`, payload);
  }

  bulkMessageToday(payload: { organization_id: number, message_template?: string, branch_id?: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/appointments/bulk-message-today`, payload);
  }

  sendMessage(payload: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/organization/message/send`, payload);
  }

  getCustomerHistory(query: { phone?: string, name?: string }): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/v1/customers/history`, { params: query });
  }
}
