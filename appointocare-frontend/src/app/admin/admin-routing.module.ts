import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { OrganizationsComponent } from './components/organizations/organizations.component';
import { SubscriptionsComponent } from './components/subscriptions/subscriptions.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { AdminDashboardComponent } from './components/dashboard/admin-dashboard.component';
import { PlatformAdminComponent } from './components/platform/platform-admin.component';

const routes: Routes = [
  {
    path: '',
    component: AdminDashboardComponent
  },
  { path: 'organizations', component: OrganizationsComponent },
  { path: 'subscriptions', component: SubscriptionsComponent },
  { path: 'transactions', component: TransactionsComponent }
  , { path: 'platform', component: PlatformAdminComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
