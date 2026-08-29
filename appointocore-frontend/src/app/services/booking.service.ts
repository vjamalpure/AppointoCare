import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BookingService {
  constructor(private http: HttpClient) {}

  getBookings(orgId: number, date: string): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/organizations/${orgId}/bookings?date=${date}`);
  }

  cancelBooking(orgId: number, bookingId: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/organizations/${orgId}/bookings/${bookingId}/cancel`, {});
  }

  rescheduleBooking(orgId: number, bookingId: number, payload: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/organizations/${orgId}/bookings/${bookingId}`, payload);
  }
}
