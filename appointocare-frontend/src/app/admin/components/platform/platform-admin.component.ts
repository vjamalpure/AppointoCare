import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-platform-admin',
  templateUrl: './platform-admin.component.html',
  styleUrls: ['./platform-admin.component.scss']
})
export class PlatformAdminComponent implements OnInit {
  plans: any[] = [];
  templates: any[] = [];
  envConfig: any = null;
  whatsappConfig: any = null;
  paymentConfig: any = null;
  secretsStatus: any = null;
  savingKey = false;
  savingWhatsApp = false;
  savingPayment = false;

  constructor(
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.platform.getPlans().subscribe(data => this.plans = data);
    this.platform.getTemplates().subscribe(data => this.templates = data);
    this.platform.getEnvConfig().subscribe(data => this.envConfig = data);
    this.platform.getWhatsAppConfig().subscribe(data => this.whatsappConfig = data);
    this.platform.getPaymentConfig().subscribe(data => this.paymentConfig = data);
    this.platform.getSecretsStatus().subscribe(data => this.secretsStatus = data);
  }

  saveEnvConfig(): void {
    this.savingKey = true;
    this.platform.updateEnvConfig({
      subscription_provider_key: this.envConfig.subscription_provider_key,
      subscription_tier: this.envConfig.subscription_tier
    }).subscribe({
      next: () => {
        this.savingKey = false;
        this.snackBar.open('External subscription configuration saved!', 'Dismiss', { duration: 3000 });
      },
      error: () => {
        this.savingKey = false;
        this.snackBar.open('Failed to save subscription config', 'Dismiss', { duration: 3000 });
      }
    });
  }

  saveWhatsApp(): void {
    this.savingWhatsApp = true;
    this.platform.updateWhatsAppConfig(this.whatsappConfig).subscribe({
      next: () => {
        this.savingWhatsApp = false;
        this.snackBar.open('WhatsApp Meta Cloud API settings updated!', 'Dismiss', { duration: 3000 });
      },
      error: () => {
        this.savingWhatsApp = false;
        this.snackBar.open('Failed to update WhatsApp settings', 'Dismiss', { duration: 3000 });
      }
    });
  }

  savePayment(): void {
    this.savingPayment = true;
    this.platform.updatePaymentConfig(this.paymentConfig).subscribe({
      next: () => {
        this.savingPayment = false;
        this.snackBar.open('Razorpay payment gateway settings updated!', 'Dismiss', { duration: 3000 });
      },
      error: () => {
        this.savingPayment = false;
        this.snackBar.open('Failed to update Razorpay settings', 'Dismiss', { duration: 3000 });
      }
    });
  }

  getServiceName(s: any): string {
    if (!s) return '';
    return typeof s === 'string' ? s : (s.name || JSON.stringify(s));
  }
}
