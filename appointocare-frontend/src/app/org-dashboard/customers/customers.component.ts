import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-customers',
  templateUrl: './customers.component.html',
  styleUrls: ['./customers.component.scss']
})
export class CustomersComponent implements OnInit {
  customers: any[] = [];
  filteredCustomers: any[] = [];
  searchTerm = '';
  selectedTag = 'ALL';
  loading = false;

  // Selected customer timeline modal/drawer
  selectedCustomer: any = null;
  customerTimeline: any = null;
  loadingTimeline = false;

  // New Customer Dialog
  showAddDialog = false;
  newCustomer: any = {
    name: '',
    phone: '',
    email: '',
    gender: 'Female',
    address: '',
    tags: 'General',
    notes: ''
  };

  tags = ['ALL', 'VIP', 'General', 'Dental', 'Preventive', 'Corporate'];

  constructor(
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadCustomers();
  }

  loadCustomers(): void {
    this.loading = true;
    this.platform.getCustomers().subscribe({
      next: (data) => {
        this.customers = data;
        this.applyFilter();
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Failed to load customers', 'Dismiss', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  applyFilter(): void {
    let list = [...this.customers];

    if (this.selectedTag !== 'ALL') {
      list = list.filter(c => (c.tags || '').includes(this.selectedTag));
    }

    if (this.searchTerm.trim()) {
      const q = this.searchTerm.toLowerCase();
      list = list.filter(c =>
        c.name.toLowerCase().includes(q) ||
        c.phone.includes(q) ||
        (c.email && c.email.toLowerCase().includes(q))
      );
    }

    this.filteredCustomers = list;
  }

  viewCustomer(customer: any): void {
    this.selectedCustomer = customer;
    this.loadingTimeline = true;
    this.platform.getCustomerTimeline(customer.id).subscribe({
      next: (data) => {
        this.customerTimeline = data;
        this.loadingTimeline = false;
      },
      error: () => {
        this.customerTimeline = {
          customer,
          appointments: [],
          transactions: [],
          messages: []
        };
        this.loadingTimeline = false;
      }
    });
  }

  closeTimeline(): void {
    this.selectedCustomer = null;
    this.customerTimeline = null;
  }

  openAddDialog(): void {
    this.newCustomer = {
      name: '',
      phone: '+1 ',
      email: '',
      gender: 'Female',
      address: '',
      tags: 'General',
      notes: ''
    };
    this.showAddDialog = true;
  }

  createCustomer(): void {
    if (!this.newCustomer.name || !this.newCustomer.phone) {
      this.snackBar.open('Name and phone are required', 'Dismiss', { duration: 2500 });
      return;
    }

    this.platform.createCustomer(this.newCustomer).subscribe({
      next: (created: any) => {
        this.snackBar.open(`Customer ${created.name || 'record'} added!`, 'Dismiss', { duration: 3000 });
        this.showAddDialog = false;
        this.loadCustomers();
      },
      error: () => {
        this.snackBar.open('Failed to create customer', 'Dismiss', { duration: 3000 });
      }
    });
  }

  deleteCustomer(id: number, event: Event): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to remove this customer profile?')) {
      this.platform.deleteCustomer(id).subscribe({
        next: () => {
          this.snackBar.open('Customer removed', 'Dismiss', { duration: 2500 });
          if (this.selectedCustomer?.id === id) {
            this.closeTimeline();
          }
          this.loadCustomers();
        }
      });
    }
  }
}
