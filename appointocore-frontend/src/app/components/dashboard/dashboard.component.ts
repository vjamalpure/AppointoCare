import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { AuthService } from '../../auth/auth.service';
import { AppointmentService } from '../../services/appointments.service';

export interface Appointment {
  id: number;
  customer_name: string;
  customer_phone: string;
  appointment_date: string;
  status: string;
  payment_status: string;
  amount?: number;
  payment_method?: string;
  transaction_status?: string;
  created_at: string;
  updated_at?: string | null;
}

export interface DashboardData {
  organization: { name: string; sector: string; subscription_status: string };
  appointments: Appointment[];
  appointments_count: number;
  transactions: any[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  @Output() organizationNameChange = new EventEmitter<string>();

  dashboardData: DashboardData = {
    organization: { name: '', sector: '', subscription_status: '' },
    appointments: [],
    appointments_count: 0,
    transactions: []
  };

  loading = true;
  role: string | null = null;

  showModal = false;
  editAppointment: Appointment | null = null;
  editAppointmentDateTime: string = '';

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private appointmentService: AppointmentService
  ) {}

  ngOnInit(): void {
    this.role = this.authService.getUserRole();
    this.loadDashboard();
  }

  loadDashboard() {
    this.loading = true;
    this.dashboardService.getDashboard(this.role!).subscribe({
      next: (data: DashboardData) => {
        this.dashboardData = data;
        this.dashboardData.appointments = data.appointments || [];
        this.dashboardData.appointments_count = data.appointments_count || 0;

        const orgName = data?.organization?.name?.trim();
        if (orgName) this.organizationNameChange.emit(orgName);

        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching dashboard:', err);
        this.loading = false;
      }
    });
  }

  closeModal() {
    this.showModal = false;
    this.editAppointment = null;
    this.editAppointmentDateTime = '';
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString();
  }

  openEditModal(appt: Appointment) {
    this.editAppointment = { ...appt };
    this.editAppointment.payment_status = this.editAppointment.payment_status || 'Pending';
    this.editAppointmentDateTime = this.formatForInput(appt.appointment_date);
    this.showModal = true;
  }

  formatForInput(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  saveEdit() {
    if (!this.editAppointment) return;

    this.appointmentService.updateAppointment(this.editAppointment.id, {
      appointment_date: this.editAppointmentDateTime,
      payment_status: this.editAppointment.payment_status,
      status: this.editAppointment.status
    }).subscribe({
      next: () => {
        this.closeModal();
        this.loadDashboard();
      },
      error: (err) => console.error('Update failed:', err)
    });
  }

  updateAppointment(apptId: number, status?: string, paymentStatus?: string, appointmentDate?: string) {
  if (!apptId) return;

  const updateData: any = {};
  if (status) updateData.status = status;
  if (paymentStatus) updateData.payment_status = paymentStatus;
  if (appointmentDate) updateData.appointment_date = appointmentDate;

  this.appointmentService.updateAppointment(apptId, updateData).subscribe({
    next: () => {
      alert('Appointment updated successfully!');
      this.loadDashboard(); // Refresh dashboard to reflect changes
    },
    error: (err) => {
      console.error('Failed to update appointment:', err);
      alert('Failed to update appointment. Please try again.');
    }
  });
}


  updateAppointmentStatus(apptId: number, status: string) {
    if (!status) return;
    this.appointmentService.updateAppointment(apptId, { status }).subscribe({
      next: () => this.loadDashboard(),
      error: (err) => console.error('Status update failed:', err)
    });
  }

  // Stats getters
  getTotalAppointments(): number { return this.dashboardData.appointments_count || 0; }
  getBookedCount(): number { return this.dashboardData.appointments.filter(a => a.status === 'Booked').length; }
  getCompletedCount(): number { return this.dashboardData.appointments.filter(a => a.status === 'Completed').length; }
  getCancelledCount(): number { return this.dashboardData.appointments.filter(a => a.status === 'Cancelled').length; }
  getTotalPaid(): number { return this.dashboardData.appointments.filter(a => a.payment_status === 'Paid').length; }
  getTotalUnpaid(): number { return this.dashboardData.appointments.filter(a => a.payment_status === 'Pending').length; }

  getApptStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'booked': return '#f9d77f';
      case 'completed': return '#68d391';
      case 'cancelled': return '#fc8181';
      default: return '#e0e6ed';
    }
  }
}
