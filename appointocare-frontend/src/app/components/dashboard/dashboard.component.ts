import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { AuthService } from '../../auth/auth.service';
import { AppointmentService } from '../../services/appointments.service';
import { IndustryService } from '../../services/industry.service';

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

  // Industry Operational Command Strip
  sectorStats: any = null;
  sectorBenchmarks: any = null;
  sectorIcon = 'domain';
  sectorLabel = 'Operations';

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private appointmentService: AppointmentService,
    private industryService: IndustryService
  ) {}

  ngOnInit(): void {
    this.role = this.authService.getUserRole();
    this.loadDashboard();
    this.loadSectorStats();
  }

  loadSectorStats(): void {
    const sector = this.industryService.getSector();
    const config = this.industryService.getConfig(sector);
    this.sectorIcon = config?.icon || 'domain';
    this.sectorLabel = sector || 'Operations';

    this.industryService.getSectorStats().subscribe({
      next: (stats) => { this.sectorStats = stats; },
      error: () => {}
    });
    this.industryService.getBenchmarks().subscribe({
      next: (b) => { this.sectorBenchmarks = b?.benchmarks || null; },
      error: () => {}
    });
  }

  loadDashboard() {
    this.loading = true;
    const effectiveRole = this.role || 'Organization';
    this.dashboardService.getDashboard(effectiveRole).subscribe({
      next: (data: any) => {
        let appts: Appointment[] = [];
        let count = 0;
        if (Array.isArray(data?.appointments)) {
          appts = data.appointments;
          count = data.appointments_count || appts.length;
        } else if (data?.appointments && typeof data.appointments === 'object') {
          count = data.appointments.total || 0;
        }

        this.dashboardData = {
          organization: data?.organization || { name: '', sector: '', subscription_status: '' },
          appointments: appts,
          appointments_count: count,
          transactions: Array.isArray(data?.transactions) ? data.transactions : []
        };

        const orgName = this.dashboardData.organization?.name?.trim();
        if (orgName) this.organizationNameChange.emit(orgName);

        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching dashboard:', err);
        this.dashboardData = {
          organization: { name: '', sector: '', subscription_status: '' },
          appointments: [],
          appointments_count: 0,
          transactions: []
        };
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

  editDate: Date = new Date();
  editTime: string = '10:00 AM';
  timeSlots: string[] = [
    '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM',
    '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM',
    '05:00 PM', '05:30 PM', '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM'
  ];

  openEditModal(appt: Appointment) {
    this.editAppointment = { ...appt };
    this.editAppointment.payment_status = this.editAppointment.payment_status || 'Pending';
    if (appt.appointment_date) {
      const d = new Date(appt.appointment_date);
      this.editDate = d;
      let h = d.getHours();
      const m = d.getMinutes() >= 30 ? '30' : '00';
      const ampm = h >= 12 ? 'PM' : 'AM';
      if (h > 12) h -= 12;
      if (h === 0) h = 12;
      const hStr = h.toString().padStart(2, '0');
      this.editTime = `${hStr}:${m} ${ampm}`;
    } else {
      this.editDate = new Date();
      this.editTime = '10:00 AM';
    }
    this.showModal = true;
  }

  formatEditDateTime(): string {
    const d = this.editDate ? new Date(this.editDate) : new Date();
    const timeMatch = (this.editTime || '10:00 AM').match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
    let hours = 10;
    let minutes = 0;
    if (timeMatch) {
      hours = parseInt(timeMatch[1], 10);
      minutes = parseInt(timeMatch[2], 10);
      const ampm = timeMatch[3].toUpperCase();
      if (ampm === 'PM' && hours < 12) hours += 12;
      if (ampm === 'AM' && hours === 12) hours = 0;
    }
    d.setHours(hours, minutes, 0, 0);
    return d.toISOString();
  }

  saveEdit() {
    if (!this.editAppointment) return;

    this.appointmentService.updateAppointment(this.editAppointment.id, {
      appointment_date: this.formatEditDateTime(),
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
  getTotalAppointments(): number { return this.dashboardData?.appointments_count || 0; }
  getBookedCount(): number { return (this.dashboardData?.appointments || []).filter(a => a?.status === 'Booked').length; }
  getCompletedCount(): number { return (this.dashboardData?.appointments || []).filter(a => a?.status === 'Completed').length; }
  getCancelledCount(): number { return (this.dashboardData?.appointments || []).filter(a => a?.status === 'Cancelled').length; }
  getTotalPaid(): number { return (this.dashboardData?.appointments || []).filter(a => a?.payment_status === 'Paid').length; }
  getTotalUnpaid(): number { return (this.dashboardData?.appointments || []).filter(a => a?.payment_status === 'Pending' || a?.payment_status === 'Unpaid').length; }

  getApptStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'booked': return '#f9d77f';
      case 'completed': return '#68d391';
      case 'cancelled': return '#fc8181';
      default: return '#e0e6ed';
    }
  }
}
