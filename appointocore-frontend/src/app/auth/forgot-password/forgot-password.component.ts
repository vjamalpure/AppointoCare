import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss']
})
export class ForgotPasswordComponent {
  username = '';
  role: 'Admin' | 'Organization' = 'Organization';
  code = '';
  message = '';
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  submit() {
    this.error = '';
    this.message = '';
    this.loading = true;

    this.authService.forgotPassword(this.username, this.role, this.role === 'Organization' ? this.code : undefined)
      .subscribe({
        next: (res: any) => {
          this.message = res?.msg || 'If the account exists, a reset token was generated.';
          this.loading = false;
        },
        error: (err: any) => {
          this.error = err?.error?.msg || 'Unable to request password reset.';
          this.loading = false;
        }
      });
  }
}
