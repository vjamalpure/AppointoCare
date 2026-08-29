import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

// Appointment summary returned by backend
export interface AppointmentSummary {
  total: number;
  booked: number;
  completed: number;
  cancelled: number;
}

// Payment summary returned by backend
export interface PaymentSummary {
  total_paid: number;
  total_unpaid: number;
}

// Individual appointment (only for admin dashboard)
export interface Appointment {
  id: number;
  customer_name: string;
  customer_phone: string;
  appointment_date: string;
  status: string;
  payment_status: string;
  created_at: string;
  updated_at: string | null;
}

export interface Transaction {
  id: number;
  amount: number;
  created_at: string;
  status: string;
  transaction_type: string;
}

export interface DashboardData {
  organization: {
    name: string;
    sector: string;
    subscription_status: string;
  };
  appointments: Appointment[];
  appointments_count: number;
  transactions: Transaction[];
}


@Injectable({ providedIn: 'root' })
export class DashboardService {

  constructor(private http: HttpClient) {}

  getDashboard(role: string): Observable<DashboardData> {
    const url =
      role === 'Admin'
        ? `${environment.apiUrl}/admin/dashboard`
        : `${environment.apiUrl}/organization/dashboard`;

    return this.http.get<DashboardData>(url);
  }

  getOrganizationTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/transactions/all`);
  }
}
