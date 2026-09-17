import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';

// From src/app/components/org-dashboard -> up two levels to src/app/material.module.ts
import { MaterialModule } from '../material.module';
import { SharedModule } from '../components/shared/shared.module';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { OrgDashboardRoutingModule } from './org-dashboard-routing.module';
import { OrgDashboardComponent } from './org-dashboard.component';
import { OrgBookingsComponent } from './bookings/bookings.component';
import { OrgTransactionsComponent } from './transactions/transactions.component';
import { OrgProfileComponent } from './profile/profile.component';
import { OrgSubscriptionComponent } from './subscription/subscription.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';
import { PlatformWorkspaceComponent } from '../platform/platform-workspace.component';
import { OrgBranchesComponent } from './branches/branches.component';
import { CustomersComponent } from './customers/customers.component';
import { ServicesComponent } from './services/services.component';
import { WhatsAppChatComponent } from './whatsapp/whatsapp-chat.component';
import { StaffComponent } from './staff/staff.component';

@NgModule({
  declarations: [
    OrgDashboardComponent,
    DashboardComponent,
    OrgBookingsComponent,
    OrgTransactionsComponent,
    OrgProfileComponent,
    OrgSubscriptionComponent,
    PlatformWorkspaceComponent,
    OrgBranchesComponent,
    CustomersComponent,
    ServicesComponent,
    WhatsAppChatComponent,
    StaffComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    SharedModule,
    OrgDashboardRoutingModule,
    RouterModule,
    FormsModule,
    BaseChartDirective,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatProgressBarModule
  ],
  exports: [
    OrgDashboardComponent
  ]
})
export class OrgDashboardModule {}