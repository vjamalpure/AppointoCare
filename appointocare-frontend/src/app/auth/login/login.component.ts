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
  rememberMe = false;
  loading = false;
  errorMsg = '';

  selectedRole: 'admin' | 'organization' = 'organization';
  currentYear: number = new Date().getFullYear();

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit(loginForm: NgForm) {
    // Prevent submission if form is invalid
    if (!loginForm.valid) return;

    this.loading = true;
    this.errorMsg = '';

    // For admin, clear org code
    const orgCode = this.selectedRole === 'organization' ? this.organization_code : '';

    // Call AuthService login
    this.auth.login(this.username, this.password, orgCode, this.rememberMe)
      .subscribe({
        next: (res: any) => {
          if (!res?.access_token) {
            this.errorMsg = 'Invalid response from server';
            this.loading = false;
            return;
          }

          this.auth.saveOrgName(res?.organization_name, this.rememberMe);

          // Decode token to get role
          const role = this.auth.getUserRole();

          // Redirect based on role
          if (role === 'Admin') {
            this.router.navigate(['/admin-dashboard']);
          } else if (role === 'Organization') {
            this.router.navigate(['/org-dashboard']);
          } else {
            this.errorMsg = 'User role not recognized';
          }
        },
        error: (err) => {
          this.errorMsg = err?.error?.msg || 'Invalid credentials';
        },
        complete: () => {
          this.loading = false;
        }
      });
  }
}
