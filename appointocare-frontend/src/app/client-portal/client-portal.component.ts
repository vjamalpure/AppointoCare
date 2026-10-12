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

  constructor(
    private portalService: ClientPortalService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const savedToken = localStorage.getItem('appointocare_portal_token');
    if (savedToken) {
      this.sessionToken = savedToken;
      this.loadOverview();
    }
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
        localStorage.setItem('appointocare_portal_token', this.sessionToken);
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
      },
      error: (err) => {
        this.isLoadingOverview = false;
        this.isAuthenticated = false;
        localStorage.removeItem('appointocare_portal_token');
        this.snackBar.open('Session expired. Please log in again.', 'Close', { duration: 3000 });
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
    localStorage.removeItem('appointocare_portal_token');
    this.snackBar.open('Signed out of Client Portal', 'OK', { duration: 2500 });
  }
}
