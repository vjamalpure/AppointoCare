import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.scss']
})
export class SubscriptionsComponent implements OnInit {
  subscriptions: any[] = [];
  displayedColumns: string[] = ['id', 'organization', 'plan', 'startDate', 'endDate', 'nextBilling', 'status', 'actions'];

  constructor(private adminService: AdminService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadSubscriptions();
  }

  loadSubscriptions() {
    this.adminService.getSubscriptions().subscribe({
      next: data => this.subscriptions = data,
      error: () => this.snackBar.open('Error loading subscriptions', 'Close', { duration: 3000 })
    });
  }

  updateSubscriptionStatus(subscription: any, status: string) {
    const body = { subscription_status: status };
    this.adminService.updateOrganization(subscription.organization_id, body).subscribe({
      next: () => {
        this.snackBar.open(`Subscription ${status.toLowerCase()} successfully`, 'Close', { duration: 3000 });
        this.loadSubscriptions();
      },
      error: () => this.snackBar.open('Error updating subscription status', 'Close', { duration: 3000 })
    });
  }

  renewSubscription(subscription: any) {
    const today = new Date();
    const endDate = new Date();
    endDate.setDate(today.getDate() + 30);
    const body = {
      subscription_status: 'Active',
      subscription_start: today.toISOString(),
      subscription_end: endDate.toISOString(),
      next_billing_date: endDate.toISOString()
    };

    this.adminService.updateOrganization(subscription.organization_id, body).subscribe({
      next: () => {
        this.snackBar.open('Subscription renewed successfully', 'Close', { duration: 3000 });
        this.loadSubscriptions();
      },
      error: () => this.snackBar.open('Error renewing subscription', 'Close', { duration: 3000 })
    });
  }
}
