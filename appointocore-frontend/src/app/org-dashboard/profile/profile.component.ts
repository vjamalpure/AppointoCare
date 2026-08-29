import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { MatFormField } from "@angular/material/form-field";

@Component({
  selector: 'app-org-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class OrgProfileComponent implements OnInit {
  profile: any = {};
  editMode = false;
  loading = false;
  message = '';

  constructor(private dashboardService: DashboardService, private http: HttpClient) {}

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    this.loading = true;
    this.dashboardService.getDashboard('Organization').subscribe({
      next: (data) => {
        this.profile = data.organization || {};
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  enableEdit() {
    this.editMode = true;
    this.message = '';
  }

  cancelEdit() {
    this.editMode = false;
    this.loadProfile();
  }

  saveProfile() {
    this.loading = true;
    const token = localStorage.getItem('appointocore_token');
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const body = {
      name: this.profile.name,
      subscription_plan: this.profile.subscription?.plan,
      subscription_status: this.profile.subscription?.status
    };
    this.http.patch(`${environment.apiUrl}/organization/update`, body, { headers }).subscribe({
      next: () => {
        this.message = 'Profile updated successfully.';
        this.editMode = false;
        this.loading = false;
        this.loadProfile();
      },
      error: () => {
        this.message = 'Error updating profile.';
        this.loading = false;
      }
    });
  }
}
