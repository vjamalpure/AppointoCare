import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-staff',
  templateUrl: './staff.component.html',
  styleUrls: ['./staff.component.scss']
})
export class StaffComponent implements OnInit {
  staffList: any[] = [];
  loading = false;
  showDialog = false;
  isEditMode = false;

  currentStaff: any = {
    name: '',
    username: '',
    email: '',
    phone: '',
    role: 'Staff',
    is_active: true
  };

  roles = [
    { name: 'Organization Admin', val: 'Organization' },
    { name: 'Organization Manager', val: 'Organization Manager' },
    { name: 'Staff / Front Desk', val: 'Staff' },
    { name: 'Specialist / Consultant', val: 'Specialist' }
  ];

  constructor(
    private platform: PlatformService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadStaff();
  }

  loadStaff(): void {
    this.loading = true;
    this.platform.getStaff().subscribe({
      next: (data) => {
        this.staffList = data;
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Failed to load staff members', 'Dismiss', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  openCreateDialog(): void {
    this.isEditMode = false;
    this.currentStaff = {
      name: '',
      username: '',
      email: '',
      phone: '+1 ',
      role: 'Staff',
      is_active: true
    };
    this.showDialog = true;
  }

  openEditDialog(staff: any): void {
    this.isEditMode = true;
    this.currentStaff = { ...staff };
    this.showDialog = true;
  }

  saveStaff(): void {
    if (!this.currentStaff.name || !this.currentStaff.email) {
      this.snackBar.open('Please provide staff name and email', 'Dismiss', { duration: 2500 });
      return;
    }

    if (this.isEditMode) {
      this.platform.updateStaff(this.currentStaff.id, this.currentStaff).subscribe({
        next: () => {
          this.snackBar.open('Staff member updated', 'Dismiss', { duration: 2500 });
          this.showDialog = false;
          this.loadStaff();
        }
      });
    } else {
      if (!this.currentStaff.username) {
        this.currentStaff.username = this.currentStaff.email.split('@')[0];
      }
      this.platform.createStaff(this.currentStaff).subscribe({
        next: () => {
          this.snackBar.open('Staff member added to organization', 'Dismiss', { duration: 2500 });
          this.showDialog = false;
          this.loadStaff();
        }
      });
    }
  }

  toggleActive(staff: any): void {
    const updated = !staff.is_active;
    this.platform.updateStaff(staff.id, { is_active: updated }).subscribe({
      next: () => {
        staff.is_active = updated;
        this.snackBar.open(`Account ${updated ? 'Activated' : 'Suspended'}`, 'Dismiss', { duration: 2000 });
      }
    });
  }

  deleteStaff(id: number): void {
    if (confirm('Revoke access and delete this staff user?')) {
      this.platform.deleteStaff(id).subscribe({
        next: () => {
          this.snackBar.open('Staff user removed', 'Dismiss', { duration: 2000 });
          this.loadStaff();
        }
      });
    }
  }

  getRoleBadgeClass(role: string): string {
    const r = (role || '').toLowerCase();
    if (r.includes('admin')) return 'role-admin';
    if (r.includes('manager')) return 'role-manager';
    if (r.includes('specialist')) return 'role-specialist';
    return 'role-staff';
  }
}
