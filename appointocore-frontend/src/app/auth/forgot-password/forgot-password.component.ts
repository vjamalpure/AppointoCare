import { Component } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss']
})
export class ForgotPasswordComponent {
  username = '';
  role = 'Organization';
  code = '';
  loading = false;
  message = '';
  error = '';

  constructor(private authService: AuthService) {}

  submit(): void {
    if (!this.username) return;
    this.loading = true;
    this.message = '';
    this.error = '';

    const payload: { username: string; role: string; code?: string } = {
      username: this.username,
      role: this.role
    };
    if (this.role === 'Organization' && this.code) {
      payload.code = this.code;
    }

    this.authService.forgotPassword(payload).subscribe({
      next: (res: any) => {
        this.loading = false;
        this.message = res?.msg || 'Recovery instructions have been sent successfully.';
      },
      error: (err: any) => {
        this.loading = false;
        this.error = err?.error?.msg || 'Failed to send recovery request. Please check credentials.';
      }
    });
  }
}
