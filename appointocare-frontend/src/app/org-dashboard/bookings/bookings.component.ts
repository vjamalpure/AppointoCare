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
  bookingDate: Date = new Date();
  bookingTime: string = '10:00 AM';
  timeSlots: string[] = [
    '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM',
    '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM',
    '05:00 PM', '05:30 PM', '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM'
  ];

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

  formatSelectedDateTime(): string {
    const d = this.bookingDate ? new Date(this.bookingDate) : new Date();
    const timeMatch = (this.bookingTime || '10:00 AM').match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
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

  createBooking() {
    if (!this.newBooking.customer_name || !this.newBooking.customer_phone || !this.bookingDate || !this.bookingTime) {
      this.snackBar.open(`Please fill all required ${this.terms.customerLabel} details`, 'Close', { duration: 3000 });
      return;
    }

    // Combine interactive calendar date and clock time slot
    const appointmentDateIso = this.formatSelectedDateTime();

    // Format custom fields summary into notes
    const customSummary = Object.entries(this.customData)
      .filter(([_, val]) => val)
      .map(([key, val]) => {
        const def = this.customFields.find(f => f.key === key);
        return `${def ? def.label : key}: ${val}`;
      })
      .join(' | ');

    const orgId = this.authService.getOrganizationId();
    const payload: any = {
      ...this.newBooking,
      appointment_date: appointmentDateIso,
      notes: customSummary ? `${this.newBooking.notes ? this.newBooking.notes + ' [' + customSummary + ']' : customSummary}` : this.newBooking.notes
    };
    if (orgId) {
      payload.organization_id = parseInt(orgId, 10);
    }

    this.appointmentService.createAppointment(payload).subscribe({
      next: () => {
        this.snackBar.open(`${this.terms.appointmentLabel} booked successfully`, 'OK', { duration: 3000 });
        this.showBookingModal = false;
        this.customData = {};
        this.bookingDate = new Date();
        this.bookingTime = '10:00 AM';
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
      error: (err) => {
        const msg = err?.error?.msg || `Failed to book ${this.terms.appointmentLabel.toLowerCase()}`;
        this.snackBar.open(msg, 'Close', { duration: 3000 });
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
