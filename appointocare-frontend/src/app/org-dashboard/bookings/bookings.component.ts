import { Component, OnInit } from '@angular/core';
import { AppointmentService } from '../../services/appointments.service';
import { AuthService } from '../../auth/auth.service';
import { IndustryService } from '../../services/industry.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-bookings',
  templateUrl: './bookings.component.html',
  styleUrls: ['./bookings.component.scss']
})
export class OrgBookingsComponent implements OnInit {
  bookings: any[] = [];
  displayedColumns: string[] = ['id', 'patient', 'service', 'schedule', 'status', 'payment_status', 'actions'];
  loading = false;
  message = '';
  searchTerm: string = '';
  selectedStatus: string = 'ALL';

  // Multi-Industry Engine Bindings
  sector: string = 'Healthcare';
  terms: any;
  config: any;
  customFields: any[] = [];
  customData: Record<string, any> = {};

  showBookingModal = false;
  newBooking: any = {
    customer_name: '',
    customer_phone: '',
    service_name: '',
    appointment_date: '',
    amount: 60,
    payment_status: 'Pending',
    status: 'Booked',
    notes: ''
  };

  constructor(
    private appointmentService: AppointmentService,
    private authService: AuthService,
    public industryService: IndustryService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadSectorData();
    this.loadBookings();
  }

  loadSectorData() {
    this.sector = this.industryService.getSector();
    this.terms = this.industryService.getTerms(this.sector);
    this.config = this.industryService.getConfig(this.sector);
    this.customFields = this.industryService.getCustomFields(this.sector);

    if (this.config?.servicePresets?.length) {
      this.newBooking.service_name = this.config.servicePresets[0].name;
      this.newBooking.amount = this.config.servicePresets[0].price;
    }
  }

  onServiceSelect(serviceName: string) {
    const preset = this.config?.servicePresets?.find((s: any) => s.name === serviceName);
    if (preset) {
      this.newBooking.amount = preset.price;
    }
  }

  loadBookings() {
    this.loading = true;
    const role = this.authService.getUserRole();
    this.appointmentService.getAppointments(role || 'Organization').subscribe({
      next: (data) => {
        this.bookings = Array.isArray(data) ? data : (Array.isArray(data?.appointments) ? data.appointments : []);
        this.loading = false;
      },
      error: () => {
        this.bookings = [];
        this.loading = false;
      }
    });
  }

  get filteredBookings(): any[] {
    let list = this.bookings || [];
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      list = list.filter(b =>
        b.customer_name?.toLowerCase().includes(term) ||
        b.customer_phone?.includes(term) ||
        b.service_name?.toLowerCase().includes(term) ||
        b.notes?.toLowerCase().includes(term)
      );
    }
    if (this.selectedStatus !== 'ALL') {
      list = list.filter(b => b.status === this.selectedStatus);
    }
    return list;
  }

  get totalCount(): number {
    return this.bookings.length;
  }

  get bookedCount(): number {
    return this.bookings.filter(b => b.status === 'Booked').length;
  }

  get completedCount(): number {
    return this.bookings.filter(b => b.status === 'Completed').length;
  }

  get cancelledCount(): number {
    return this.bookings.filter(b => b.status === 'Cancelled').length;
  }

  createBooking() {
    if (!this.newBooking.customer_name || !this.newBooking.customer_phone || !this.newBooking.appointment_date) {
      this.snackBar.open(`Please fill all required ${this.terms.customerLabel} details`, 'Close', { duration: 3000 });
      return;
    }

    // Format custom fields summary into notes
    const customSummary = Object.entries(this.customData)
      .filter(([_, val]) => val)
      .map(([key, val]) => {
        const def = this.customFields.find(f => f.key === key);
        return `${def ? def.label : key}: ${val}`;
      })
      .join(' | ');

    const payload = {
      ...this.newBooking,
      notes: customSummary ? `${this.newBooking.notes ? this.newBooking.notes + ' [' + customSummary + ']' : customSummary}` : this.newBooking.notes
    };

    this.appointmentService.createAppointment(payload).subscribe({
      next: () => {
        this.snackBar.open(`${this.terms.appointmentLabel} booked successfully`, 'OK', { duration: 3000 });
        this.showBookingModal = false;
        this.customData = {};
        this.newBooking = {
          customer_name: '',
          customer_phone: '',
          service_name: this.config?.servicePresets?.[0]?.name || 'Consultation',
          appointment_date: '',
          amount: this.config?.servicePresets?.[0]?.price || 60,
          payment_status: 'Pending',
          status: 'Booked',
          notes: ''
        };
        this.loadBookings();
      },
      error: () => {
        this.snackBar.open(`Failed to book ${this.terms.appointmentLabel.toLowerCase()}`, 'Close', { duration: 3000 });
      }
    });
  }

  sendReminder(booking: any) {
    const formattedDate = new Date(booking.appointment_date).toLocaleString();
    const message = `Hello ${booking.customer_name}, your ${this.terms.appointmentLabel.toLowerCase()} for ${booking.service_name || this.terms.serviceLabel} is confirmed for ${formattedDate}. Please arrive 10 minutes prior.`;
    this.appointmentService.sendMessage({
      recipient_number: booking.customer_phone,
      message_content: message,
      message_type: 'WhatsApp',
      related_appointment_id: booking.id,
      remarks: `${this.terms.appointmentLabel} reminder sent via WhatsApp`
    }).subscribe({
      next: () => {
        this.snackBar.open(`WhatsApp reminder sent to ${booking.customer_phone}`, 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('WhatsApp message gateway notified', 'OK', { duration: 3000 });
      }
    });
  }

  updateStatus(booking: any, status: string) {
    this.appointmentService.updateAppointment(booking.id, { status }).subscribe({
      next: () => {
        booking.status = status;
        this.snackBar.open(`${this.terms.appointmentLabel} marked as ${status}`, 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Could not update booking status.', 'Close', { duration: 3000 });
      }
    });
  }
}
