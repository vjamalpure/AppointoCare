import { Component, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-organizations',
  templateUrl: './organizations.component.html',
  styleUrls: ['./organizations.component.scss']
})
export class OrganizationsComponent implements OnInit {
  organizations: any[] = [];
  selectedOrg: any = null;
  orgUsers: any[] = [];
  newOrg: any = {
    name: '',
    code: '',
    sector: '',
    username: '',
    password: '',
    subscription_plan: 'Basic',
    subscription_status: 'Active'
  };
  newUser: any = { username: '', password: '', role: 'Staff' };
  userEdit: any = null;
  displayedColumns: string[] = ['id', 'name', 'code', 'plan', 'status', 'users', 'actions'];

  constructor(private adminService: AdminService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadOrganizations();
  }

  loadOrganizations() {
    this.adminService.getOrganizations().subscribe({
      next: data => this.organizations = data,
      error: () => this.snackBar.open('Error loading organizations', 'Close', { duration: 3000 })
    });
  }

  selectOrganization(org: any) {
    this.selectedOrg = org;
    this.loadOrganizationUsers(org.id);
  }

  loadOrganizationUsers(orgId: number) {
    this.adminService.getOrganizationUsers(orgId).subscribe({
      next: data => this.orgUsers = data,
      error: () => this.snackBar.open('Error loading organization users', 'Close', { duration: 3000 })
    });
  }

  createOrganization() {
    this.adminService.createOrganization(this.newOrg).subscribe({
      next: () => {
        this.snackBar.open('Organization created', 'Close', { duration: 3000 });
        this.newOrg = { name: '', code: '', sector: '', username: '', password: '', subscription_plan: 'Basic', subscription_status: 'Active' };
        this.loadOrganizations();
      },
      error: () => this.snackBar.open('Error creating organization', 'Close', { duration: 3000 })
    });
  }

  updateOrganization() {
    if (!this.selectedOrg) return;
    this.adminService.updateOrganization(this.selectedOrg.id, this.selectedOrg).subscribe({
      next: () => this.snackBar.open('Organization updated', 'Close', { duration: 3000 }),
      error: () => this.snackBar.open('Error updating organization', 'Close', { duration: 3000 })
    });
  }

  deleteOrganization(org: any) {
    if (!confirm('Delete organization?')) {
      return;
    }
    this.adminService.deleteOrganization(org.id).subscribe({
      next: () => {
        this.snackBar.open('Organization deleted', 'Close', { duration: 3000 });
        this.loadOrganizations();
        if (this.selectedOrg?.id === org.id) {
          this.selectedOrg = null;
          this.orgUsers = [];
        }
      },
      error: () => this.snackBar.open('Error deleting organization', 'Close', { duration: 3000 })
    });
  }

  addUser() {
    if (!this.selectedOrg) return;
    this.adminService.createOrganizationUser(this.selectedOrg.id, this.newUser).subscribe({
      next: () => {
        this.snackBar.open('User created', 'Close', { duration: 3000 });
        this.newUser = { username: '', password: '', role: 'Staff' };
        this.loadOrganizationUsers(this.selectedOrg.id);
      },
      error: () => this.snackBar.open('Error creating user', 'Close', { duration: 3000 })
    });
  }

  editUser(user: any) {
    this.userEdit = { ...user };
  }

  saveUser() {
    if (!this.selectedOrg || !this.userEdit) return;
    const body: any = {
      username: this.userEdit.username,
      role: this.userEdit.role,
      is_active: this.userEdit.is_active
    };
    if (this.userEdit.password) {
      body.password = this.userEdit.password;
    }
    this.adminService.updateOrganizationUser(this.selectedOrg.id, this.userEdit.id, body).subscribe({
      next: () => {
        this.snackBar.open('User updated', 'Close', { duration: 3000 });
        this.userEdit = null;
        this.loadOrganizationUsers(this.selectedOrg.id);
      },
      error: () => this.snackBar.open('Error updating user', 'Close', { duration: 3000 })
    });
  }

  cancelEditUser() {
    this.userEdit = null;
  }

  deleteUser(user: any) {
    if (!this.selectedOrg || !confirm('Delete this user?')) return;
    this.adminService.deleteOrganizationUser(this.selectedOrg.id, user.id).subscribe({
      next: () => {
        this.snackBar.open('User deleted', 'Close', { duration: 3000 });
        this.loadOrganizationUsers(this.selectedOrg.id);
      },
      error: () => this.snackBar.open('Error deleting user', 'Close', { duration: 3000 })
    });
  }
}
