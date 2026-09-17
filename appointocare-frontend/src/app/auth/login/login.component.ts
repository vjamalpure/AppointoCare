import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { IndustryService } from '../../services/industry.service';
import { Router } from '@angular/router';
import { NgForm } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  organization_code = 'ORG1';
  username = 'org1';
  password = 'Org@12345';
  rememberMe = true;
  loading = false;
  errorMsg = '';
  showPassword = false;

  selectedRole: 'admin' | 'organization' | 'staff' = 'organization';
  currentYear: number = new Date().getFullYear();

  industryPresets = [
    { label: '🏥 Healthcare (ORG1)', sector: 'Healthcare', org: 'City Care Health & Dental', user: 'org1', pass: 'Org@12345', code: 'ORG1', role: 'organization' as const },
    { label: '💇 Salon & Spa (ORG2)', sector: 'Salon', org: 'Apex Aesthetics & Wellness Spa', user: 'org2', pass: 'Org@12345', code: 'ORG2', role: 'organization' as const },
    { label: '📈 Wealth & Finance (ORG3)', sector: 'Finance', org: 'Vanguard Wealth Advisory', user: 'org3', pass: 'Org@12345', code: 'ORG3', role: 'organization' as const },
    { label: '🛡️ Insurance (ORG4)', sector: 'Insurance', org: 'Sovereign Life Insurance', user: 'org4', pass: 'Org@12345', code: 'ORG4', role: 'organization' as const },
    { label: '👔 Luxury Retail (ORG5)', sector: 'Retail', org: 'Aura Haute Couture & Styling', user: 'org5', pass: 'Org@12345', code: 'ORG5', role: 'organization' as const },
    { label: '🎓 Education (ORG6)', sector: 'Education', org: 'Beacon Global University Counseling', user: 'org6', pass: 'Org@12345', code: 'ORG6', role: 'organization' as const },
    { label: '⚖️ Legal & Consult (ORG7)', sector: 'Legal', org: 'Sterling & Blackwood Legal', user: 'org7', pass: 'Org@12345', code: 'ORG7', role: 'organization' as const },
    { label: '🏛️ Real Estate (ORG8)', sector: 'RealEstate', org: 'Sovereign Realty & Architecture', user: 'org8', pass: 'Org@12345', code: 'ORG8', role: 'organization' as const },
    { label: '🌐 Enterprise (ORG9)', sector: 'Enterprise', org: 'Vanguard Global Enterprise', user: 'org9', pass: 'Org@12345', code: 'ORG9', role: 'organization' as const },
    { label: '🩺 Dr. Sarah (Doctor)', sector: 'Healthcare', org: 'Chief Surgeon', user: 'doc_sarah', pass: 'Staff@12345', code: 'ORG1', role: 'staff' as const },
    { label: '🏛️ Marcus (Realtor)', sector: 'RealEstate', org: 'Managing Broker', user: 'marcus_realty', pass: 'Staff@12345', code: 'ORG8', role: 'staff' as const },
    { label: '🌐 Elizabeth (Consultant)', sector: 'Enterprise', org: 'Principal Consultant', user: 'elizabeth_exec', pass: 'Staff@12345', code: 'ORG9', role: 'staff' as const }
  ];

  constructor(
    private auth: AuthService,
    private industry: IndustryService,
    private router: Router
  ) {}

  setRole(role: 'admin' | 'organization' | 'staff'): void {
    this.selectedRole = role;
    this.errorMsg = '';
    if (role === 'admin') {
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

  selectPreset(preset: any): void {
    this.selectedRole = preset.role;
    this.username = preset.user;
    this.password = preset.pass;
    this.organization_code = preset.code;
    this.errorMsg = '';
    if (preset.sector) {
      this.industry.setSector(preset.sector);
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  clearError(): void {
    this.errorMsg = '';
  }

  onSubmit(loginForm: NgForm): void {
    if (!loginForm.valid) return;

    this.loading = true;
    this.errorMsg = '';

    const orgCode = this.selectedRole !== 'admin' ? this.organization_code?.trim() : '';
    const cleanUsername = this.username?.trim();
    const cleanPassword = this.password;

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

  fillAdminDemo(): void {
    this.setRole('admin');
  }

  fillOrgDemo(): void {
    this.setRole('organization');
  }

  fillStaffDemo(): void {
    this.setRole('staff');
  }
}
