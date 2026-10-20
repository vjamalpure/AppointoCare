import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss']
})
export class ResetPasswordComponent {
  token = '';
  newPassword = '';
  confirmPassword = '';
  loading = false;
  message = '';
  error = '';

  constructor(private authService: AuthService, private router: Router) {}

  submit(): void {
    if (!this.token || !this.newPassword || !this.confirmPassword) {
      return;
    }
    if (this.newPassword !== this.confirmPassword) {
      this.error = 'Passwords do not match.';
      return;
    }

    this.loading = true;
    this.message = '';
    this.error = '';

    this.authService.resetPassword({ token: this.token, new_password: this.newPassword }).subscribe({
      next: (res: any) => {
        this.loading = false;
        this.message = res?.msg || 'Password updated successfully! Redirecting to sign in...';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 1500);
      },
      error: (err: any) => {
        this.loading = false;
        this.error = err?.error?.msg || 'Failed to update password. Invalid or expired token.';
      }
    });
  }
}
