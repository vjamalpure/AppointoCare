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

const routes: Routes = [
  {
    path: '',
    component: OrgDashboardComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', component: DashboardComponent },
      { path: 'bookings', component: OrgBookingsComponent },
      { path: 'transactions', component: OrgTransactionsComponent },
      { path: 'profile', component: OrgProfileComponent },
      { path: 'subscription', component: OrgSubscriptionComponent }
      ,{ path: 'workspace', component: PlatformWorkspaceComponent }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrgDashboardRoutingModule {}
