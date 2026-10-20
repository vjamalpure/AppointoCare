import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { IndustryService } from '../../services/industry.service';
import { Router } from '@angular/router';
import { NgForm } from '@angular/forms';

export interface SampleCredential {
  title: string;
  role: 'organization' | 'staff' | 'superadmin';
  roleBadge: string;
  code: string;
  user: string;
  pass: string;
  desc: string;
  sector?: string;
}

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  organization_code = 'ORG1';
  username = 'org1';
  password = 'Org@12345';
  rememberMe = true;
  loading = false;
  errorMsg = '';
  showPassword = false;

  selectedRole: 'organization' | 'staff' | 'superadmin' = 'organization';
  currentYear: number = new Date().getFullYear();

  // Dark / Night Mode Support
  isDarkMode = false;

  // Modals & Popups
  showCredentialsModal = false;
  activeInfoModal: 'integrations' | 'license' | 'terms' | 'blog' | 'register' | 'features' | null = null;
  copyToastMsg = '';
  private toastTimer: any = null;

  // New Demo Registration Form State
  registerData = {
    clinicName: '',
    ownerName: '',
    email: '',
    sector: 'Healthcare',
    phone: '',
    submitted: false
  };

  sampleCredentials: SampleCredential[] = [
    {
      title: 'Platform SuperAdmin',
      role: 'superadmin',
      roleBadge: 'SuperAdmin Master',
      code: '',
      user: 'superadmin',
      pass: 'Admin@12345',
      desc: 'Master platform controls, analytics, multi-tenant governance & audit.'
    },
    {
      title: 'Healthcare Clinic Admin (ORG1)',
      role: 'organization',
      roleBadge: 'Clinic Owner / Admin',
      code: 'ORG1',
      user: 'org1',
      pass: 'Org@12345',
      desc: 'City Care Health & Dental: services, staff schedules, patients & billing.',
      sector: 'Healthcare'
    },
    {
      title: 'Dr. Sarah (Clinical Specialist)',
      role: 'staff',
      roleBadge: 'Doctor / Specialist',
      code: 'ORG1',
      user: 'doc_sarah',
      pass: 'Staff@12345',
      desc: 'Chief Surgeon / Specialist schedule, active bookings & consult notes.',
      sector: 'Healthcare'
    },
    {
      title: 'Aesthetics & Wellness Spa (ORG2)',
      role: 'organization',
      roleBadge: 'Salon & Spa Admin',
      code: 'ORG2',
      user: 'org2',
      pass: 'Org@12345',
      desc: 'Apex Aesthetics Spa: stylist bookings, formulation lookbooks & packages.',
      sector: 'Salon'
    },
    {
      title: 'Vanguard Wealth Advisory (ORG3)',
      role: 'organization',
      roleBadge: 'Finance & Wealth Admin',
      code: 'ORG3',
      user: 'org3',
      pass: 'Org@12345',
      desc: 'Financial advisory client consultations, retainer ledgers & reviews.',
      sector: 'Finance'
    }
  ];

  constructor(
    private auth: AuthService,
    private industry: IndustryService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const savedTheme = localStorage.getItem('appointocare_theme');
    this.isDarkMode = savedTheme === 'dark';
  }

  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
    localStorage.setItem('appointocare_theme', this.isDarkMode ? 'dark' : 'light');
    this.showToast(this.isDarkMode ? '🌙 Night mode activated' : '☀️ Day mode activated');
  }

  setRole(role: 'organization' | 'staff' | 'superadmin'): void {
    this.selectedRole = role;
    this.errorMsg = '';
    if (role === 'superadmin') {
      this.username = 'superadmin';
      this.password = 'Admin@12345';
      this.organization_code = '';
    } else if (role === 'organization') {
      this.username = 'org1';
      this.password = 'Org@12345';
      this.organization_code = 'ORG1';
    } else if (role === 'staff') {
      this.username = 'doc_sarah';
      this.password = 'Staff@12345';
      this.organization_code = 'ORG1';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  clearError(): void {
    this.errorMsg = '';
  }

  toggleCredentialsModal(open?: boolean): void {
    this.showCredentialsModal = open !== undefined ? open : !this.showCredentialsModal;
  }

  openInfoModal(modalType: 'integrations' | 'license' | 'terms' | 'blog' | 'register' | 'features'): void {
    this.activeInfoModal = modalType;
  }

  closeInfoModal(): void {
    this.activeInfoModal = null;
  }

  handleRegisterSubmit(): void {
    if (!this.registerData.clinicName || !this.registerData.email) return;
    this.registerData.submitted = true;
    setTimeout(() => {
      this.showToast('✓ Demo workspace created! Please sign in with sample credentials.');
      this.closeInfoModal();
      this.registerData.submitted = false;
      this.setRole('organization');
    }, 1200);
  }

  copyAndApply(cred: SampleCredential): void {
    this.selectedRole = cred.role;
    this.username = cred.user;
    this.password = cred.pass;
    this.organization_code = cred.code;
    this.errorMsg = '';

    if (cred.sector) {
      this.industry.setSector(cred.sector);
    }

    const copyText = cred.role === 'superadmin'
      ? `Username: ${cred.user} | Password: ${cred.pass}`
      : `Org Code: ${cred.code} | Username: ${cred.user} | Password: ${cred.pass}`;

    this.copyToClipboard(copyText);
    this.showToast(`✓ Copied ${cred.title} credentials and filled into form!`);
    this.showCredentialsModal = false;
  }

  copyToClipboard(text: string): void {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => {
        this.fallbackCopy(text);
      });
    } else {
      this.fallbackCopy(text);
    }
  }

  private fallbackCopy(text: string): void {
    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.style.position = 'fixed';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    } catch {}
  }

  copyQuickSuperAdmin(): void {
    const superAdminCred = this.sampleCredentials.find(c => c.role === 'superadmin');
    if (superAdminCred) {
      this.copyAndApply(superAdminCred);
    }
  }

  private showToast(msg: string): void {
    this.copyToastMsg = msg;
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
    this.toastTimer = setTimeout(() => {
      this.copyToastMsg = '';
    }, 3500);
  }

  onSubmit(loginForm: NgForm): void {
    if (!loginForm.valid) return;

    this.loading = true;
    this.errorMsg = '';

    const cleanUsername = this.username?.trim();
    const cleanPassword = this.password;
    const orgCode = this.selectedRole === 'superadmin' ? undefined : (this.organization_code?.trim() || undefined);

    this.auth.login(cleanUsername, cleanPassword, orgCode, this.rememberMe)
      .subscribe({
        next: (res: any) => {
          if (!res?.access_token) {
            this.errorMsg = 'Invalid response from server';
            this.loading = false;
            return;
          }

          if (res?.organization_name) {
            this.auth.saveOrgName(res.organization_name, this.rememberMe);
          }
          if (res?.sector) {
            this.auth.saveSector(res.sector, this.rememberMe);
            this.industry.setSector(res.sector);
          }

          const role = this.auth.getUserRole();
          if (role === 'Admin' || role === 'SuperAdmin') {
            this.router.navigate(['/admin-dashboard']);
          } else {
            this.router.navigate(['/org-dashboard']);
          }
        },
        error: (err) => {
          this.errorMsg = err?.error?.msg || 'Invalid credentials or login failed';
          this.loading = false;
        },
        complete: () => {
          this.loading = false;
        }
      });
  }
}
