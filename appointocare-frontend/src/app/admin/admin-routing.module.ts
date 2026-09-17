import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { OrganizationsComponent } from './components/organizations/organizations.component';
import { SubscriptionsComponent } from './components/subscriptions/subscriptions.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { AdminDashboardComponent } from './components/dashboard/admin-dashboard.component';
import { PlatformAdminComponent } from './components/platform/platform-admin.component';
import { AdminAppointmentsComponent } from './components/appointments/admin-appointments.component';
import { AdminReportsComponent } from './components/reports/admin-reports.component';
import { AuditLogsComponent } from './components/audit-logs/audit-logs.component';
import { NotificationsCenterComponent } from '../components/notifications/notifications-center.component';

const routes: Routes = [
  { path: '', component: AdminDashboardComponent },
  { path: 'notifications', component: NotificationsCenterComponent },
  { path: 'appointments', component: AdminAppointmentsComponent },
  { path: 'organizations', component: OrganizationsComponent },
  { path: 'subscriptions', component: SubscriptionsComponent },
  { path: 'transactions', component: TransactionsComponent },
  { path: 'platform', component: PlatformAdminComponent },
  { path: 'audit-logs', component: AuditLogsComponent },
  { path: 'reports', component: AdminReportsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
