import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { ChartConfiguration, ChartDataset, ChartType } from 'chart.js';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  loading = true;
  errorMsg = '';
  executiveData: any = null;

  appointments: any[] = [];
  transactions: any[] = [];

  // 1. Monthly Revenue & GMV Dual-Axis Chart
  revenueChartLabels: string[] = [];
  revenueChartData: ChartDataset<'bar'>[] = [
    {
      data: [],
      label: 'SaaS Platform Revenue (₹)',
      backgroundColor: '#4f46e5',
      borderRadius: 6,
      order: 1
    },
    {
      data: [],
      label: 'Tenant Booking GMV (₹)',
      backgroundColor: '#06b6d4',
      borderRadius: 6,
      order: 2
    }
  ];
  revenueChartOptions: ChartConfiguration['options'] = {
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
        titleFont: { family: 'Plus Jakarta Sans', weight: 'bold' },
        bodyFont: { family: 'Inter' },
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

  // 2. Sector Distribution Doughnut Chart
  sectorChartLabels: string[] = [];
  sectorChartData: ChartDataset<'doughnut'>[] = [
    {
      data: [],
      backgroundColor: [
        '#4f46e5', '#06b6d4', '#10b981', '#f59e0b',
        '#f43f5e', '#8b5cf6', '#3b82f6', '#ec4899', '#64748b'
      ],
      borderWidth: 2,
      borderColor: '#ffffff',
      hoverOffset: 6
    }
  ];
  sectorChartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: { color: '#334155', font: { family: 'Inter', size: 11 } }
      }
    },
    cutout: '68%'
  };

  constructor(
    private adminService: AdminService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadExecutiveAnalytics();
    this.loadRecentAppointments();
    this.loadRecentTransactions();
  }

  loadExecutiveAnalytics(): void {
    this.loading = true;
    this.errorMsg = '';

    this.adminService.getExecutiveDashboardAnalytics().subscribe({
      next: (data) => {
        this.executiveData = data;
        this.populateCharts(data);
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load executive analytics:', err);
        this.errorMsg = 'Failed to load live platform analytics. Falling back to core metrics.';
        this.loading = false;
      }
    });
  }

  populateCharts(data: any): void {
    if (!data) return;

    // Monthly history
    if (Array.isArray(data.monthly_revenue_history)) {
      this.revenueChartLabels = data.monthly_revenue_history.map((m: any) => m.month_label);
      this.revenueChartData[0].data = data.monthly_revenue_history.map((m: any) => m.saas_revenue || 0);
      this.revenueChartData[1].data = data.monthly_revenue_history.map((m: any) => m.tenant_gmv || 0);
    }

    // Sector distribution
    if (Array.isArray(data.sector_distribution)) {
      this.sectorChartLabels = data.sector_distribution.map((s: any) => s.sector);
      this.sectorChartData[0].data = data.sector_distribution.map((s: any) => s.organizations_count || 0);
    }
  }

  loadRecentAppointments(): void {
    this.http.get<any[]>(`${environment.apiUrl}/admin/appointments`).subscribe({
      next: (data) => {
        this.appointments = Array.isArray(data) ? data.slice(0, 5) : [];
      },
      error: () => {
        this.appointments = [];
      }
    });
  }

  loadRecentTransactions(): void {
    this.http.get<any[]>(`${environment.apiUrl}/admin/transactions`).subscribe({
      next: (data) => {
        this.transactions = Array.isArray(data) ? data.slice(0, 5) : [];
      },
      error: () => {
        this.transactions = [];
      }
    });
  }
}
