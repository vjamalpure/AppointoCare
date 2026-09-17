import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../../services/platform.service';
import { IndustryService } from '../../../services/industry.service';
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

  // Multi-Industry Benchmarking & Add-on Engine state
  allBenchmarks: Record<string, any> = {};
  allAddonsCatalog: Record<string, any> = {};
  allIndustryRecords: any[] = [];
  selectedSector: string = 'Healthcare';
  sectorsList: string[] = [
    'Healthcare',
    'Salon',
    'Finance',
    'Insurance',
    'Retail',
    'Education',
    'Consultancy',
    'Real Estate',
    'Professional Services'
  ];

  constructor(
    private platform: PlatformService,
    public industryService: IndustryService,
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

    // Multi-Industry Engine
    this.industryService.getBenchmarks(true).subscribe({
      next: (res) => this.allBenchmarks = res.all_benchmarks || {}
    });
    this.industryService.getAddons(undefined, true).subscribe({
      next: (res) => this.allAddonsCatalog = res.sectors || {}
    });
    this.industryService.getRecords({ all: true }).subscribe({
      next: (res) => this.allIndustryRecords = res || []
    });
  }

  selectSector(sector: string): void {
    this.selectedSector = sector;
  }

  getSectorIcon(sector: string): string {
    switch (sector) {
      case 'Healthcare': return 'medical_services';
      case 'Salon': return 'spa';
      case 'Finance': return 'account_balance';
      case 'Retail': return 'shopping_bag';
      case 'Insurance': return 'verified_user';
      case 'Education': return 'school';
      case 'Consultancy': return 'gavel';
      case 'Real Estate': return 'apartment';
      case 'Professional Services': return 'business_center';
      default: return 'domain';
    }
  }

  getSectorRecordCount(sector: string): number {
    return this.allIndustryRecords.filter(r => r.sector === sector || (sector === 'Salon' && r.sector.includes('Salon'))).length;
  }

  getRecordsForSector(sector: string): any[] {
    return this.allIndustryRecords.filter(r => r.sector === sector || (sector === 'Salon' && r.sector.includes('Salon')));
  }

  getCurrentSectorBenchmarks(): any {
    return this.allBenchmarks[this.selectedSector] || null;
  }

  getCurrentSectorAddons(): any[] {
    return this.allAddonsCatalog[this.selectedSector] || [];
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
