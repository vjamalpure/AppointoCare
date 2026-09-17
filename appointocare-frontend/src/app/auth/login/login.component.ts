import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { NgForm } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  organization_code = '';
  username = '';
  password = '';
  rememberMe = true;
  loading = false;
  errorMsg = '';
  showPassword = false;

  selectedRole: 'admin' | 'organization' = 'organization';
  currentYear: number = new Date().getFullYear();

  constructor(private auth: AuthService, private router: Router) {}

  setRole(role: 'admin' | 'organization'): void {
    this.selectedRole = role;
    this.errorMsg = '';
    if (role === 'admin') {
      this.organization_code = '';
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

    const orgCode = this.selectedRole === 'organization' ? this.organization_code?.trim() : '';
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

          this.auth.saveOrgName(res?.organization_name, this.rememberMe);

          const role = this.auth.getUserRole();

          if (role === 'Admin' || role === 'SuperAdmin') {
            this.router.navigate(['/admin']);
          } else if (role === 'Organization' || role === 'Manager' || role === 'Staff') {
            this.router.navigate(['/org-dashboard']);
          } else {
            this.errorMsg = `User role '${role}' not recognized`;
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
    this.username = 'superadmin';
    this.password = 'Admin@12345';
    this.organization_code = '';
    this.errorMsg = '';
  }

  fillOrgDemo(): void {
    this.setRole('organization');
    this.organization_code = 'ORG1';
    this.username = 'org1';
    this.password = 'Org@12345';
    this.errorMsg = '';
  }

  fillStaffDemo(): void {
    this.setRole('organization');
    this.organization_code = 'ORG1';
    this.username = 'staff1';
    this.password = 'Staff@12345';
    this.errorMsg = '';
  }
}
