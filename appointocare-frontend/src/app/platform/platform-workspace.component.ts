import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../services/platform.service';

@Component({
  selector: 'app-platform-workspace',
  templateUrl: './platform-workspace.component.html',
  styleUrls: ['./platform-workspace.component.scss']
})
export class PlatformWorkspaceComponent implements OnInit {
  activeTab = 'reports';
  report: any = {};
  campaigns: any[] = [];
  notifications: any[] = [];
  branches: any[] = [];
  plans: any[] = [];
  templates: any[] = [];
  campaign = { name: '', channel: 'WhatsApp', message: '' };
  branch = { name: '', address: '', phone: '' };

  constructor(private platform: PlatformService) {}

  ngOnInit(): void {
    this.loadOrganizationData();
  }

  loadOrganizationData(): void {
    this.platform.getReportSummary().subscribe(data => this.report = data);
    this.platform.getCampaigns().subscribe(data => this.campaigns = data);
    this.platform.getNotifications().subscribe(data => this.notifications = data);
    this.platform.getBranches().subscribe(data => this.branches = data);
  }

  createCampaign(): void {
    if (!this.campaign.name || !this.campaign.message) return;
    this.platform.createCampaign(this.campaign).subscribe(() => {
      this.campaign = { name: '', channel: 'WhatsApp', message: '' };
      this.loadOrganizationData();
    });
  }

  createBranch(): void {
    if (!this.branch.name) return;
    this.platform.createBranch(this.branch).subscribe(() => {
      this.branch = { name: '', address: '', phone: '' };
      this.loadOrganizationData();
    });
  }

  markRead(id: number): void {
    this.platform.markNotificationRead(id).subscribe(() => this.loadOrganizationData());
  }
}
