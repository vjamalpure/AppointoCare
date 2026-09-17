import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-admin-reports',
  templateUrl: './admin-reports.component.html',
  styleUrls: ['./admin-reports.component.scss']
})
export class AdminReportsComponent implements OnInit {
  loading = false;
  summary: any = {
    total_revenue: 124500,
    monthly_growth: 14.8,
    active_tenants: 8,
    total_appointments_this_month: 248,
    completion_rate: 94.2
  };
  monthlyData: any[] = [];
  maxMonthlyVal: number = 1;

  constructor(
    private adminService: AdminService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.adminService.getReportsSummary().subscribe({
      next: (data) => {
        if (data) this.summary = data;
      },
      error: () => {}
    });

    this.adminService.getMonthlyTransactionSummary().subscribe({
      next: (data) => {
        this.monthlyData = data || [];
        this.maxMonthlyVal = Math.max(...this.monthlyData.map(d => d.total || 0), 1);
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Error loading reports', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  getMonthName(monthNum: number): string {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[monthNum - 1] || `M${monthNum}`;
  }
}
