import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChartConfiguration, ChartDataset } from 'chart.js';

@Component({
  selector: 'app-admin-reports',
  templateUrl: './admin-reports.component.html',
  styleUrls: ['./admin-reports.component.scss']
})
export class AdminReportsComponent implements OnInit {
  loading = false;
  analyticsData: any = null;

  // Chart.js Configuration
  monthlyChartLabels: string[] = [];
  monthlyChartData: ChartDataset<'bar'>[] = [
    {
      data: [],
      label: 'SaaS Platform Revenue (₹)',
      backgroundColor: '#4f46e5',
      borderRadius: 6
    },
    {
      data: [],
      label: 'Tenant Booking GMV (₹)',
      backgroundColor: '#06b6d4',
      borderRadius: 6
    }
  ];
  monthlyChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: { color: '#334155', font: { family: 'Inter', size: 12, weight: 600 } }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } }
      },
      y: {
        grid: { color: 'rgba(226, 232, 240, 0.6)' },
        ticks: {
          color: '#64748b',
          font: { family: 'Inter', size: 11 },
          callback: (value) => '₹' + Number(value).toLocaleString()
        }
      }
    }
  };

  constructor(
    private adminService: AdminService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.adminService.getExecutiveDashboardAnalytics().subscribe({
      next: (data) => {
        this.analyticsData = data;
        if (Array.isArray(data?.monthly_revenue_history)) {
          this.monthlyChartLabels = data.monthly_revenue_history.map((m: any) => m.month_label);
          this.monthlyChartData[0].data = data.monthly_revenue_history.map((m: any) => m.saas_revenue || 0);
          this.monthlyChartData[1].data = data.monthly_revenue_history.map((m: any) => m.tenant_gmv || 0);
        }
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Error loading live platform reports', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }
}
