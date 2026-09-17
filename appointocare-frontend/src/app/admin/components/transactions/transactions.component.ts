import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class TransactionsComponent implements OnInit {
  transactions: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'ALL';
  displayedColumns: string[] = ['id', 'organization', 'amount', 'type', 'date', 'status'];

  constructor(private adminService: AdminService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  loadTransactions() {
    this.adminService.getTransactions().subscribe({
      next: data => this.transactions = data || [],
      error: () => this.snackBar.open('Error loading transactions', 'Close', { duration: 3000 })
    });
  }

  get filteredTransactions(): any[] {
    let list = this.transactions || [];
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      list = list.filter(t =>
        t.organization_name?.toLowerCase().includes(term) ||
        (t.id && t.id.toString().includes(term)) ||
        (t.transaction_type && t.transaction_type.toLowerCase().includes(term))
      );
    }
    if (this.selectedStatus !== 'ALL') {
      list = list.filter(t => t.status === this.selectedStatus);
    }
    return list;
  }

  get totalVolume(): number {
    return (this.transactions || []).reduce((acc, t) => acc + (Number(t.amount) || 0), 0);
  }

  get successfulCount(): number {
    return (this.transactions || []).filter(t => t.status === 'Paid' || t.status === 'Completed' || t.status === 'Success').length;
  }

  get pendingCount(): number {
    return (this.transactions || []).filter(t => t.status === 'Pending' || t.status === 'Unpaid').length;
  }
}
