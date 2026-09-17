import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-audit-logs',
  templateUrl: './audit-logs.component.html',
  styleUrls: ['./audit-logs.component.scss']
})
export class AuditLogsComponent implements OnInit {
  logs: any[] = [];
  filteredLogs: any[] = [];
  loading = false;
  selectedFilter = 'ALL';
  searchTerm = '';

  filterOptions = [
    { label: 'All Activities', value: 'ALL' },
    { label: 'Authentication', value: 'LOGIN' },
    { label: 'Bookings', value: 'BOOKING' },
    { label: 'Payments', value: 'PAYMENT' },
    { label: 'WhatsApp Bot', value: 'WHATSAPP' },
    { label: 'Settings & Config', value: 'CONFIG' }
  ];

  constructor(
    private platformService: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadLogs();
  }

  loadLogs(): void {
    this.loading = true;
    this.platformService.getAuditLogs().subscribe({
      next: (data) => {
        this.logs = data;
        this.applyFilter();
        this.loading = false;
      },
      error: (err) => {
        this.snackBar.open('Failed to load audit logs', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  applyFilter(): void {
    let list = [...this.logs];

    if (this.selectedFilter !== 'ALL') {
      list = list.filter(l => (l.action || '').toUpperCase().includes(this.selectedFilter));
    }

    if (this.searchTerm.trim()) {
      const q = this.searchTerm.toLowerCase();
      list = list.filter(l =>
        (l.user && l.user.toLowerCase().includes(q)) ||
        (l.details && l.details.toLowerCase().includes(q)) ||
        (l.ip_address && l.ip_address.includes(q)) ||
        (l.action && l.action.toLowerCase().includes(q))
      );
    }

    this.filteredLogs = list;
  }

  setFilter(filter: string): void {
    this.selectedFilter = filter;
    this.applyFilter();
  }

  getActionBadgeClass(action: string): string {
    const act = (action || '').toUpperCase();
    if (act.includes('LOGIN') || act.includes('AUTH')) return 'badge-auth';
    if (act.includes('BOOKING')) return 'badge-booking';
    if (act.includes('PAYMENT')) return 'badge-payment';
    if (act.includes('WHATSAPP')) return 'badge-whatsapp';
    return 'badge-system';
  }
}
