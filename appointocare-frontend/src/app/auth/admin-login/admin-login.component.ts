import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router, ActivatedRoute } from '@angular/router';
import { NgForm } from '@angular/forms';

@Component({
  selector: 'app-admin-login',
  templateUrl: './admin-login.component.html',
  styleUrls: ['./admin-login.component.scss']
})
export class AdminLoginComponent {
  username = 'superadmin';
  password = 'Admin@12345';
  showPassword = false;
  loading = false;
  errorMsg = '';
  rememberMe = true;
  returnUrl = '/admin-dashboard';
  currentYear = new Date().getFullYear();

  adminPresets = [
    {
      label: '👑 Master Platform SuperAdmin',
      role: 'SuperAdmin',
      user: 'superadmin',
      pass: 'Admin@12345',
      desc: 'Platform analytics, tenant controls, commissions & audit'
    }
  ];

  selectPreset(preset: any): void {
    this.username = preset.user;
    this.password = preset.pass;
    this.errorMsg = '';
  }

  constructor(
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    const returnParam = this.route.snapshot.queryParams['returnUrl'];
    if (returnParam && !returnParam.includes('//')) {
      this.returnUrl = returnParam;
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  clearError(): void {
    this.errorMsg = '';
  }

  onSubmit(form: NgForm): void {
    if (!form.valid) return;

    this.loading = true;
    this.errorMsg = '';

    const cleanUsername = this.username?.trim();
    const cleanPassword = this.password;

    // SuperAdmin does not supply an organization code
    this.auth.login(cleanUsername, cleanPassword, undefined, this.rememberMe).subscribe({
      next: (res: any) => {
        if (!res?.access_token) {
          this.errorMsg = 'Invalid administrative credentials';
          this.loading = false;
          return;
        }

        const role = this.auth.getUserRole();
        if (role === 'Admin' || role === 'SuperAdmin') {
          this.router.navigateByUrl(this.returnUrl);
        } else {
          this.auth.logout();
          this.errorMsg = 'Administrative authorization required. Tenant credentials cannot access the Super Admin console.';
          this.loading = false;
        }
      },
      error: (err) => {
        this.errorMsg = err?.error?.msg || 'Administrative authentication failed. Please verify credentials.';
        this.loading = false;
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}
