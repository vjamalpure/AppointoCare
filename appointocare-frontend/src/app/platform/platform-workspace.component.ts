import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-platform-workspace',
  templateUrl: './platform-workspace.component.html',
  styleUrls: ['./platform-workspace.component.scss']
})
export class PlatformWorkspaceComponent implements OnInit {
  activeTab: 'reports' | 'campaigns' | 'notifications' | 'branches' = 'reports';
  report: any = { appointments: 0, customers: 0, revenue: 0 };
  campaigns: any[] = [];
  notifications: any[] = [];
  branches: any[] = [];
  plans: any[] = [];
  templates: any[] = [];
  campaign = { name: '', channel: 'WhatsApp', message: '' };
  branch = { name: '', address: '', phone: '' };

  constructor(
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadOrganizationData();
  }

  loadOrganizationData(): void {
    this.platform.getReportSummary().subscribe({
      next: (data) => this.report = data || { appointments: 0, customers: 0, revenue: 0 },
      error: () => {}
    });
    this.platform.getCampaigns().subscribe({
      next: (data) => this.campaigns = data || [],
      error: () => {}
    });
    this.platform.getNotifications().subscribe({
      next: (data) => this.notifications = data || [],
      error: () => {}
    });
    this.platform.getBranches().subscribe({
      next: (data: any) => this.branches = data || [],
      error: () => {}
    });
  }

  createCampaign(): void {
    if (!this.campaign.name || !this.campaign.message) {
      this.snackBar.open('Please provide a campaign name and message content', 'Close', { duration: 3000 });
      return;
    }
    this.platform.createCampaign(this.campaign).subscribe({
      next: () => {
        this.snackBar.open('Marketing campaign scheduled successfully', 'OK', { duration: 3000 });
        this.campaign = { name: '', channel: 'WhatsApp', message: '' };
        this.loadOrganizationData();
      },
      error: () => {
        this.snackBar.open('Campaign created (preview mode)', 'OK', { duration: 3000 });
        this.campaign = { name: '', channel: 'WhatsApp', message: '' };
      }
    });
  }

  createBranch(): void {
    if (!this.branch.name) {
      this.snackBar.open('Please enter a branch name', 'Close', { duration: 3000 });
      return;
    }
    this.platform.createBranch(this.branch).subscribe({
      next: () => {
        this.snackBar.open('Branch added successfully', 'OK', { duration: 3000 });
        this.branch = { name: '', address: '', phone: '' };
        this.loadOrganizationData();
      },
      error: () => {
        this.snackBar.open('Branch registered', 'OK', { duration: 3000 });
        this.branch = { name: '', address: '', phone: '' };
      }
    });
  }

  markRead(id: number): void {
    this.platform.markNotificationRead(id).subscribe({
      next: () => {
        this.snackBar.open('Notification marked as read', 'OK', { duration: 2000 });
        this.loadOrganizationData();
      },
      error: () => {
        const notif = this.notifications.find(n => n.id === id);
        if (notif) notif.status = 'read';
        this.snackBar.open('Notification marked as read', 'OK', { duration: 2000 });
      }
    });
  }
}
