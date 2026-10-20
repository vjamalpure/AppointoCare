import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-admin-appointments',
  templateUrl: './admin-appointments.component.html',
  styleUrls: ['./admin-appointments.component.scss']
})
export class AdminAppointmentsComponent implements OnInit {
  appointments: any[] = [];
  filteredAppointments: any[] = [];
  loading = false;

  searchTerm: string = '';
  selectedStatus: string = 'ALL';
  selectedPaymentStatus: string = 'ALL';

  displayedColumns: string[] = [
    'id',
    'customer',
    'organization',
    'service',
    'date',
    'status',
    'payment_status',
    'actions'
  ];

  newAppointment = {
    customer_name: '',
    customer_phone: '',
    service_name: '',
    appointment_date: '',
    notes: '',
    status: 'Booked',
    payment_status: 'Unpaid'
  };
  showAddForm = false;

  constructor(
    private adminService: AdminService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadAppointments();
  }

  loadAppointments(): void {
    this.loading = true;
    this.adminService.getAppointments().subscribe({
      next: (data) => {
        this.appointments = data || [];
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Failed to load appointments', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.appointments];

    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(a =>
        (a.customer_name && a.customer_name.toLowerCase().includes(term)) ||
        (a.customer_phone && a.customer_phone.includes(term)) ||
        (a.service_name && a.service_name.toLowerCase().includes(term)) ||
        (a.organization_name && a.organization_name.toLowerCase().includes(term))
      );
    }

    if (this.selectedStatus !== 'ALL') {
      filtered = filtered.filter(a => a.status === this.selectedStatus);
    }

    if (this.selectedPaymentStatus !== 'ALL') {
      filtered = filtered.filter(a => a.payment_status === this.selectedPaymentStatus);
    }

    this.filteredAppointments = filtered;
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  updateStatus(appt: any, newStatus: string): void {
    this.adminService.updateAppointment(appt.id, { status: newStatus }).subscribe({
      next: (updated) => {
        appt.status = newStatus;
        this.applyFilters();
        this.snackBar.open(`Appointment #${appt.id} marked as ${newStatus}`, 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to update status', 'Close', { duration: 3000 });
      }
    });
  }

  updatePaymentStatus(appt: any, newPayment: string): void {
    this.adminService.updateAppointment(appt.id, { payment_status: newPayment }).subscribe({
      next: () => {
        appt.payment_status = newPayment;
        this.applyFilters();
        this.snackBar.open(`Payment status updated to ${newPayment}`, 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to update payment status', 'Close', { duration: 3000 });
      }
    });
  }

  deleteAppointment(id: number): void {
    if (!confirm(`Are you sure you want to delete appointment #${id}?`)) return;

    this.adminService.deleteAppointment(id).subscribe({
      next: () => {
        this.appointments = this.appointments.filter(a => a.id !== id);
        this.applyFilters();
        this.snackBar.open(`Appointment #${id} removed`, 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to delete appointment', 'Close', { duration: 3000 });
      }
    });
  }

  get totalCount(): number {
    return this.appointments?.length || 0;
  }

  get bookedCount(): number {
    return (this.appointments || []).filter(a => a?.status === 'Booked').length;
  }

  get completedCount(): number {
    return (this.appointments || []).filter(a => a?.status === 'Completed').length;
  }

  get cancelledCount(): number {
    return (this.appointments || []).filter(a => a?.status === 'Cancelled').length;
  }
}
