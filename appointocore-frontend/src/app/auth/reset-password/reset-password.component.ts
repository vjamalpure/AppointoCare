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
  message = '';
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  submit() {
    this.error = '';
    this.message = '';
    if (this.newPassword !== this.confirmPassword) {
      this.error = 'Passwords do not match';
      return;
    }

    this.loading = true;
    this.authService.resetPassword(this.token, this.newPassword).subscribe({
      next: (res: any) => {
        this.message = res?.msg || 'Password updated successfully';
        this.loading = false;
      },
      error: (err: any) => {
        this.error = err?.error?.msg || 'Unable to reset password';
        this.loading = false;
      }
    });
  }
}
