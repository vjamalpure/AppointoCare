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
  displayedColumns: string[] = ['id', 'organization', 'amount', 'date', 'status'];

  constructor(private adminService: AdminService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  loadTransactions() {
    this.adminService.getTransactions().subscribe({
      next: data => this.transactions = data,
      error: () => this.snackBar.open('Error loading transactions', 'Close', { duration: 3000 })
    });
  }
}
