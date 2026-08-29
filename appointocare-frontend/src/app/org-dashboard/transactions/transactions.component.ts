import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { AuthService } from '../../auth/auth.service';
import { ChartDataset, ChartType } from 'chart.js';

@Component({
  selector: 'app-org-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class OrgTransactionsComponent implements OnInit {
  transactions: any[] = [];
  displayedColumns: string[] = ['date', 'amount', 'status', 'type'];

  // Strong typing prevents never[] issues
  transactionChartData: ChartDataset<'bar'>[] = [{ data: [], label: 'Transactions' }];
  transactionChartLabels: string[] = [];
  transactionChartOptions = { responsive: true, maintainAspectRatio: false };
  chartType: ChartType = 'bar';

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  loadTransactions(): void {
    this.dashboardService.getOrganizationTransactions().subscribe({
      next: (data) => {
        this.transactions = Array.isArray(data) ? data : [];

        const monthly: Record<string, number> = {};
        this.transactions.forEach(t => {
          const created = t?.created_at || t?.createdAt || t?.date;
          if (!created) return;
          const dt = new Date(created);
          if (isNaN(dt.getTime())) return;
          const monthLabel = dt.toLocaleString(undefined, { month: 'short', year: 'numeric' });
          const amount = Number(t.amount) || 0;
          monthly[monthLabel] = (monthly[monthLabel] || 0) + amount;
        });

        const monthLabels = Object.keys(monthly).sort((a, b) => {
          const da = new Date(a);
          const db = new Date(b);
          return da.getTime() - db.getTime();
        });

        const dataValues = monthLabels.map(m => monthly[m] || 0);

        this.transactionChartLabels = monthLabels;
        this.transactionChartData = [{ data: dataValues, label: 'Transactions' }];
      },
      error: (err) => {
        console.error('Failed loading transactions', err);
        this.transactions = [];
        this.transactionChartLabels = [];
        this.transactionChartData = [{ data: [], label: 'Transactions' }];
      }
    });
  }
}
