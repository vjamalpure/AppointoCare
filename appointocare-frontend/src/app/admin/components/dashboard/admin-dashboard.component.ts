import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  summary: any = {
    total_organizations: 0,
    active_organizations: 0,
    paused_organizations: 0,
    appointments: { total: 0, booked: 0, completed: 0, cancelled: 0 },
    total_transactions: 0,
    today_transactions: 0,
    today_transaction_amount: 0
  };
  appointments: any[] = [];
  transactions: any[] = [];
  monthlyChartData: number[] = [];
  monthlyChartLabels: string[] = [];
  maxMonthlyChartValue = 1;

  constructor(private adminService: AdminService, private http: HttpClient) {}

  ngOnInit() {
    this.loadSummary();
    this.loadAppointments();
    this.loadTransactions();
    this.loadMonthlySummary();
  }

  loadSummary() {
    this.adminService.getDashboardSummary().subscribe({
      next: (data: any) => this.summary = data,
      error: (err) => console.error('Error loading dashboard summary', err)
    });
  }

  loadAppointments() {
    this.adminService.getAppointments().subscribe({
      next: (data) => this.appointments = (data || []).slice(0, 5),
      error: (err) => console.error('Error loading appointments', err)
    });
  }

  loadTransactions() {
    this.adminService.getTransactions().subscribe({
      next: (data) => this.transactions = (data || []).slice(0, 5),
      error: (err) => console.error('Error loading transactions', err)
    });
  }

  loadMonthlySummary() {
    this.adminService.getMonthlyTransactionSummary().subscribe((data) => {
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      this.monthlyChartLabels = data.map(d => monthNames[d.month - 1]);
      this.monthlyChartData = data.map(d => d.total);
      this.maxMonthlyChartValue = Math.max(...this.monthlyChartData, 1);
    });
  }
}
