import { Component, OnInit } from '@angular/core';
import { ClientPortalService, PortalCustomerOverview } from '../services/client-portal.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-client-portal',
  templateUrl: './client-portal.component.html',
  styleUrls: ['./client-portal.component.css']
})
export class ClientPortalComponent implements OnInit {
  // Authentication State
  public isAuthenticated = false;
  public authStep: 'identifier' | 'code' = 'identifier';
  public identifier = '';
  public organizationId = 1;
  public authCode = '';
  public sessionToken = '';
  public isAuthLoading = false;

  // Portal Overview Data
  public isLoadingOverview = false;
  public overview: PortalCustomerOverview | null = null;
  public selectedTab = 0;

  // Document Upload State
  public docTitle = '';
  public docFileName = 'patient_record.pdf';
  public docContent = '';
  public isUploadingDoc = false;

  // Digital Response State
  public responseDecision = 'APPROVED';
  public responseNotes = '';
  public isSubmittingResponse = false;

  // Appointment Booking & Management State
  public availableServices: any[] = [];
  public showBookModal = false;
  public newApptService = 'General Consultation';
  public newApptDate = '';
  public newApptStaff = 'Available Specialist';
  public newApptNotes = '';
  public isBookingAppt = false;
  public rescheduleApptId: number | null = null;
  public rescheduleDate = '';
  public isRescheduling = false;

  constructor(
    private portalService: ClientPortalService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const savedToken = localStorage.getItem('appointocore_portal_token') || localStorage.getItem('appointocare_portal_token');
    if (savedToken) {
      this.sessionToken = savedToken;
      this.loadOverview();
    }
    // Set default booking date to tomorrow at 10:00 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0, 0);
    this.newApptDate = tomorrow.toISOString().slice(0, 16);
  }

  public requestCode(): void {
    if (!this.identifier.trim()) {
      this.snackBar.open('Please enter your phone number or email', 'Close', { duration: 3000 });
      return;
    }

    this.isAuthLoading = true;
    this.portalService.requestCode({
      phone: this.identifier,
      organization_id: this.organizationId
    }).subscribe({
      next: (res) => {
        this.isAuthLoading = false;
        this.sessionToken = res.session_token;
        if (res.verification_code) {
          this.authCode = res.verification_code; // autofill for effortless preview & tests
        }
        this.authStep = 'code';
        this.snackBar.open('Verification code sent!', 'OK', { duration: 3000 });
      },
      error: (err) => {
        this.isAuthLoading = false;
        const msg = err.error?.msg || 'Could not find your profile. Please check credentials.';
        this.snackBar.open(msg, 'Close', { duration: 4000 });
      }
    });
  }

  public verifyCode(): void {
    if (!this.authCode.trim()) {
      this.snackBar.open('Please enter the 6-digit verification code', 'Close', { duration: 3000 });
      return;
    }

    this.isAuthLoading = true;
    this.portalService.verifyCode({
      session_token: this.sessionToken,
      auth_code: this.authCode
    }).subscribe({
      next: (res) => {
        this.isAuthLoading = false;
        this.sessionToken = res.session_token;
        localStorage.setItem('appointocore_portal_token', this.sessionToken);
        localStorage.removeItem('appointocare_portal_token');
        this.loadOverview();
      },
      error: (err) => {
        this.isAuthLoading = false;
        const msg = err.error?.msg || 'Verification failed. Please try again.';
        this.snackBar.open(msg, 'Close', { duration: 4000 });
      }
    });
  }

  public loadOverview(): void {
    this.isLoadingOverview = true;
    this.portalService.getOverview(this.sessionToken).subscribe({
      next: (data) => {
        this.isLoadingOverview = false;
        this.isAuthenticated = true;
        this.overview = data;
        this.loadServices();
      },
      error: (err) => {
        this.isLoadingOverview = false;
        this.isAuthenticated = false;
        localStorage.removeItem('appointocore_portal_token');
        localStorage.removeItem('appointocare_portal_token');
        this.snackBar.open('Session expired. Please log in again.', 'Close', { duration: 3000 });
      }
    });
  }

  public loadServices(): void {
    if (!this.sessionToken) return;
    this.portalService.getServices(this.sessionToken).subscribe({
      next: (res) => {
        this.availableServices = res.services || [];
        if (this.availableServices.length > 0 && this.newApptService === 'General Consultation') {
          this.newApptService = this.availableServices[0].name;
        }
      }
    });
  }

  public openBookModal(): void {
    this.loadServices();
    this.showBookModal = true;
  }

  public bookAppointment(): void {
    if (!this.newApptDate) {
      this.snackBar.open('Please select an appointment date & time', 'Close', { duration: 3000 });
      return;
    }

    this.isBookingAppt = true;
    this.portalService.bookAppointment(this.sessionToken, {
      service_name: this.newApptService,
      appointment_date: this.newApptDate,
      staff_name: this.newApptStaff,
      notes: this.newApptNotes
    }).subscribe({
      next: () => {
        this.isBookingAppt = false;
        this.showBookModal = false;
        this.newApptNotes = '';
        this.snackBar.open('Appointment booked successfully!', 'OK', { duration: 3000 });
        this.loadOverview();
      },
      error: (err) => {
        this.isBookingAppt = false;
        const msg = err.error?.msg || 'Booking failed';
        this.snackBar.open(msg, 'Close', { duration: 3000 });
      }
    });
  }

  public openReschedule(appt: any): void {
    this.rescheduleApptId = appt.id;
    this.rescheduleDate = (appt.appointment_date || '').slice(0, 16);
  }

  public submitReschedule(): void {
    if (!this.rescheduleApptId || !this.rescheduleDate) return;
    this.isRescheduling = true;
    this.portalService.rescheduleAppointment(this.sessionToken, this.rescheduleApptId, {
      appointment_date: this.rescheduleDate
    }).subscribe({
      next: () => {
        this.isRescheduling = false;
        this.rescheduleApptId = null;
        this.snackBar.open('Appointment rescheduled successfully!', 'OK', { duration: 3000 });
        this.loadOverview();
      },
      error: (err) => {
        this.isRescheduling = false;
        const msg = err.error?.msg || 'Reschedule failed';
        this.snackBar.open(msg, 'Close', { duration: 3000 });
      }
    });
  }

  public cancelAppointment(apptId: number): void {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    this.portalService.cancelAppointment(this.sessionToken, apptId, {
      reason: 'Cancelled by customer via self-service portal'
    }).subscribe({
      next: () => {
        this.snackBar.open('Appointment cancelled', 'OK', { duration: 3000 });
        this.loadOverview();
      },
      error: (err) => {
        const msg = err.error?.msg || 'Cancellation failed';
        this.snackBar.open(msg, 'Close', { duration: 3000 });
      }
    });
  }

  public uploadDocument(): void {
    if (!this.docTitle.trim()) {
      this.snackBar.open('Please provide a document title', 'Close', { duration: 3000 });
      return;
    }

    this.isUploadingDoc = true;
    this.portalService.uploadDocument(this.sessionToken, {
      title: this.docTitle,
      file_name: this.docFileName,
      content: this.docContent || 'Document uploaded via secure client portal.'
    }).subscribe({
      next: () => {
        this.isUploadingDoc = false;
        this.docTitle = '';
        this.docContent = '';
        this.snackBar.open('Document uploaded successfully!', 'OK', { duration: 3000 });
        this.loadOverview();
      },
      error: (err) => {
        this.isUploadingDoc = false;
        this.snackBar.open('Failed to upload document', 'Close', { duration: 3000 });
      }
    });
  }

  public submitRecordDecision(recordId: number): void {
    this.isSubmittingResponse = true;
    this.portalService.respondToRecord(this.sessionToken, recordId, {
      decision: this.responseDecision,
      notes: this.responseNotes
    }).subscribe({
      next: () => {
        this.isSubmittingResponse = false;
        this.responseNotes = '';
        this.snackBar.open('Response submitted successfully!', 'OK', { duration: 3000 });
        this.loadOverview();
      },
      error: () => {
        this.isSubmittingResponse = false;
        this.snackBar.open('Failed to submit response', 'Close', { duration: 3000 });
      }
    });
  }

  public updatePreferences(): void {
    if (!this.overview) return;
    this.portalService.updatePreferences(this.sessionToken, {
      whatsapp: this.overview.communication_preferences.whatsapp,
      email: this.overview.communication_preferences.email,
      sms: this.overview.communication_preferences.sms || false
    }).subscribe({
      next: () => {
        this.snackBar.open('Preferences updated!', 'OK', { duration: 2500 });
      }
    });
  }

  public logout(): void {
    this.isAuthenticated = false;
    this.overview = null;
    this.authStep = 'identifier';
    this.identifier = '';
    this.authCode = '';
    this.sessionToken = '';
    localStorage.removeItem('appointocore_portal_token');
    localStorage.removeItem('appointocare_portal_token');
    this.snackBar.open('Signed out of Client Portal', 'OK', { duration: 2500 });
  }
}

