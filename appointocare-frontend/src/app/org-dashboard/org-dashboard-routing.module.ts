import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OrgDashboardComponent } from './org-dashboard.component';
import { OrgBookingsComponent } from './bookings/bookings.component';
import { OrgTransactionsComponent } from './transactions/transactions.component';
import { OrgProfileComponent } from './profile/profile.component';
import { OrgSubscriptionComponent } from './subscription/subscription.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';
import { AuthGuard } from '../guards/auth.guard';
import { PlatformWorkspaceComponent } from '../platform/platform-workspace.component';
import { OrgBranchesComponent } from './branches/branches.component';
import { CustomersComponent } from './customers/customers.component';
import { ServicesComponent } from './services/services.component';
import { WhatsAppChatComponent } from './whatsapp/whatsapp-chat.component';
import { StaffComponent } from './staff/staff.component';
import { NotificationsCenterComponent } from '../components/notifications/notifications-center.component';

const routes: Routes = [
  {
    path: '',
    component: OrgDashboardComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', component: DashboardComponent },
      { path: 'notifications', component: NotificationsCenterComponent },
      { path: 'bookings', component: OrgBookingsComponent },
      { path: 'customers', component: CustomersComponent },
      { path: 'services', component: ServicesComponent },
      { path: 'whatsapp', component: WhatsAppChatComponent },
      { path: 'staff', component: StaffComponent },
      { path: 'transactions', component: OrgTransactionsComponent },
      { path: 'profile', component: OrgProfileComponent },
      { path: 'subscription', component: OrgSubscriptionComponent },
      { path: 'workspace', component: PlatformWorkspaceComponent },
      { path: 'branches', component: OrgBranchesComponent }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrgDashboardRoutingModule {}
