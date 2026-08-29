import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PlatformService {
  private readonly url = `${environment.apiUrl}/api/v1/platform`;

  constructor(private http: HttpClient) {}

  getPlans() { return this.http.get<any[]>(`${this.url}/plans`); }
  createPlan(plan: any) { return this.http.post(`${this.url}/plans`, plan); }
  getTemplates() { return this.http.get<any[]>(`${this.url}/templates`); }
  createTemplate(template: any) { return this.http.post(`${this.url}/templates`, template); }
  getCampaigns() { return this.http.get<any[]>(`${this.url}/campaigns`); }
  createCampaign(campaign: any) { return this.http.post(`${this.url}/campaigns`, campaign); }
  getNotifications() { return this.http.get<any[]>(`${this.url}/notifications`); }
  markNotificationRead(id: number) { return this.http.post(`${this.url}/notifications/${id}/read`, {}); }
  getBranches() { return this.http.get<any[]>(`${this.url}/branches`); }
  createBranch(branch: any) { return this.http.post(`${this.url}/branches`, branch); }
  getReportSummary() { return this.http.get<any>(`${this.url}/reports/summary`); }
}
