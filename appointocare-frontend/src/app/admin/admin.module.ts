import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminRoutingModule } from './admin-routing.module';
import { MaterialModule } from '../material.module';
import { SharedModule } from '../components/shared/shared.module';
import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { OrganizationsComponent } from './components/organizations/organizations.component';
import { SubscriptionsComponent } from './components/subscriptions/subscriptions.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { AdminDashboardComponent } from './components/dashboard/admin-dashboard.component';
import { PlatformAdminComponent } from './components/platform/platform-admin.component';
import { AdminAppointmentsComponent } from './components/appointments/admin-appointments.component';
import { AdminReportsComponent } from './components/reports/admin-reports.component';
import { AuditLogsComponent } from './components/audit-logs/audit-logs.component';

@NgModule({
  declarations: [
    OrganizationsComponent,
    SubscriptionsComponent,
    TransactionsComponent,
    AdminDashboardComponent,
    PlatformAdminComponent,
    AdminAppointmentsComponent,
    AdminReportsComponent,
    AuditLogsComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    AdminRoutingModule,
    MaterialModule,
    SharedModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatProgressBarModule
  ]
})
export class AdminModule { }
