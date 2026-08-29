import { Component, OnInit } from '@angular/core';
import { AppointmentService } from '../../services/appointments.service';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-org-bookings',
  templateUrl: './bookings.component.html',
  styleUrls: ['./bookings.component.scss']
})
export class OrgBookingsComponent implements OnInit {
  bookings: any[] = [];
  displayedColumns: string[] = ['appointment_date', 'customer_name', 'customer_phone', 'status', 'payment_status', 'actions'];
  loading = false;
  message = '';

  constructor(private appointmentService: AppointmentService, private authService: AuthService) {}

  ngOnInit() {
    this.loadBookings();
  }

  loadBookings() {
    this.loading = true;
    const role = this.authService.getUserRole();
    this.appointmentService.getAppointments(role || 'Organization').subscribe({
      next: (data) => {
        this.bookings = Array.isArray(data) ? data : (data.appointments || []);
        this.loading = false;
      },
      error: () => {
        this.bookings = [];
        this.loading = false;
      }
    });
  }

  sendReminder(booking: any) {
    const message = `Hello ${booking.customer_name}, your appointment is scheduled for ${new Date(booking.appointment_date).toLocaleString()}. Please confirm.`;
    this.appointmentService.sendMessage({
      recipient_number: booking.customer_phone,
      message_content: message,
      message_type: 'WhatsApp',
      related_appointment_id: booking.id,
      remarks: 'Appointment reminder sent via WhatsApp'
    }).subscribe({
      next: () => {
        this.message = 'Reminder sent successfully.';
      },
      error: () => {
        this.message = 'Failed to send reminder.';
      }
    });
  }

  updateStatus(booking: any, status: string) {
    this.appointmentService.updateAppointment(booking.id, { status }).subscribe({
      next: () => {
        booking.status = status;
      },
      error: () => {
        this.message = 'Could not update booking status.';
      }
    });
  }
}
