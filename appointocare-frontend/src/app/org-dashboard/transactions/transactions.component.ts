import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { AuthService } from '../../auth/auth.service';
import { PlatformService } from '../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChartDataset, ChartType } from 'chart.js';

@Component({
  selector: 'app-org-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class OrgTransactionsComponent implements OnInit {
  transactions: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'ALL';
  displayedColumns: string[] = ['date', 'amount', 'type', 'status'];

  // Razorpay Quick Collection Modal
  showRazorpayModal = false;
  processingPayment = false;
  paymentForm = {
    customer_name: 'Eleanor Vance',
    amount: 85,
    service_name: 'Dental Cleaning & Oral Exam',
    appointment_id: 101
  };

  transactionChartData: ChartDataset<'bar'>[] = [{
    data: [],
    label: 'Revenue (₹)',
    backgroundColor: '#2563eb',
    borderRadius: 6
  }];
  transactionChartLabels: string[] = [];
  transactionChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        grid: { color: '#f1f5f9' },
        ticks: { color: '#64748b' }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#64748b' }
      }
    }
  };
  chartType: ChartType = 'bar';

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  openCollectPayment(): void {
    this.paymentForm = {
      customer_name: 'Eleanor Vance',
      amount: 85,
      service_name: 'Dental Cleaning & Oral Exam',
      appointment_id: 101
    };
    this.showRazorpayModal = true;
  }

  processRazorpayPayment(): void {
    this.processingPayment = true;
    this.platform.createPaymentOrder({
      amount: this.paymentForm.amount,
      customer_name: this.paymentForm.customer_name,
      appointment_id: this.paymentForm.appointment_id
    }).subscribe({
      next: (orderRes) => {
        // Auto-verify mock/live Razorpay signature
        this.platform.verifyPayment({
          razorpay_order_id: orderRes.order_id,
          razorpay_payment_id: `pay_rzp_${Date.now()}`,
          appointment_id: this.paymentForm.appointment_id,
          amount: this.paymentForm.amount,
          customer_name: this.paymentForm.customer_name
        }).subscribe({
          next: () => {
            this.processingPayment = false;
            this.showRazorpayModal = false;
            this.snackBar.open(`Payment of $${this.paymentForm.amount} processed successfully via Razorpay!`, 'Dismiss', { duration: 3500 });
            this.loadTransactions();
          },
          error: () => {
            this.processingPayment = false;
            this.snackBar.open('Razorpay verification failed', 'Dismiss', { duration: 3000 });
          }
        });
      },
      error: () => {
        this.processingPayment = false;
        this.snackBar.open('Razorpay order creation failed', 'Dismiss', { duration: 3000 });
      }
    });
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
        this.transactionChartData = [{
          data: dataValues,
          label: 'Revenue (₹)',
          backgroundColor: '#2563eb',
          borderRadius: 6
        }];
      },
      error: (err) => {
        console.error('Failed loading transactions', err);
        this.transactions = [];
        this.transactionChartLabels = [];
        this.transactionChartData = [{ data: [], label: 'Revenue (₹)' }];
      }
    });
  }

  get filteredTransactions(): any[] {
    let list = this.transactions || [];
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      list = list.filter(t =>
        (t.transaction_type && t.transaction_type.toLowerCase().includes(term)) ||
        (t.id && t.id.toString().includes(term)) ||
        (t.amount && t.amount.toString().includes(term))
      );
    }
    if (this.selectedStatus !== 'ALL') {
      list = list.filter(t => (t.status || '').toLowerCase() === this.selectedStatus.toLowerCase());
    }
    return list;
  }

  get totalRevenue(): number {
    return this.transactions.reduce((acc, t) => acc + (Number(t.amount) || 0), 0);
  }

  get successCount(): number {
    return this.transactions.filter(t => (t.status || '').toLowerCase() === 'success' || (t.status || '').toLowerCase() === 'paid').length;
  }

  get pendingCount(): number {
    return this.transactions.filter(t => (t.status || '').toLowerCase() === 'pending').length;
  }
}
