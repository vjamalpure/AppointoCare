import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-branches',
  templateUrl: './branches.component.html',
  styleUrls: ['./branches.component.scss']
})
export class OrgBranchesComponent implements OnInit {
  branches: any[] = [];
  loading = false;
  showAddModal = false;

  newBranch = {
    name: '',
    address: '',
    phone: '',
    is_main: false
  };

  constructor(private http: HttpClient, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadBranches();
  }

  loadBranches(): void {
    this.loading = true;
    this.http.get<any[]>(`${environment.apiUrl}/api/v1/platform/branches`).subscribe({
      next: (data) => {
        this.branches = data || [];
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Error loading branches', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  addBranch(): void {
    if (!this.newBranch.name.trim()) {
      this.snackBar.open('Branch name is required', 'Close', { duration: 3000 });
      return;
    }

    this.http.post(`${environment.apiUrl}/api/v1/platform/branches`, this.newBranch).subscribe({
      next: (res: any) => {
        this.branches.push(res);
        this.showAddModal = false;
        this.newBranch = { name: '', address: '', phone: '', is_main: false };
        this.snackBar.open('Branch added successfully', 'OK', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to add branch', 'Close', { duration: 3000 });
      }
    });
  }
}
