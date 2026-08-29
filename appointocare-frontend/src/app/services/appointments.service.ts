import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface AppointmentUpdate {
  status?: string;
  payment_status?: string;
  appointment_date?: string;
}

@Injectable({ providedIn: 'root' })
export class AppointmentService {
  private baseUrl = `${environment.apiUrl}/appointments`;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('appointocare_token');
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /** ✅ Get all appointments (Organization or Admin based on role) */
  getAppointments(role: string): Observable<any> {
    const headers = this.getAuthHeaders();
    const url =
      role === 'Admin'
        ? `${environment.apiUrl}/admin/appointments`
        : `${environment.apiUrl}/organization/appointments`;
    return this.http.get<any>(url, { headers });
  }

  /** ✅ Update appointment status/date/payment */
  updateAppointment(id: number, updateData: AppointmentUpdate): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.patch(`${this.baseUrl}/${id}`, updateData, { headers });
  }

  /** ✅ Delete appointment (if allowed for Admin) */
  deleteAppointment(id: number): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.delete(`${this.baseUrl}/${id}`, { headers });
  }

  /** ✅ Create a new appointment */
  createAppointment(data: any): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.post(`${this.baseUrl}`, data, { headers });
  }

  /** ✅ Get single appointment details */
  getAppointmentById(id: number): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get(`${this.baseUrl}/${id}`, { headers });
  }

  sendMessage(payload: { recipient_number: string; message_content: string; message_type?: string; related_appointment_id?: number; remarks?: string; }): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.post(`${environment.apiUrl}/organization/message/send`, payload, { headers });
  }
}
