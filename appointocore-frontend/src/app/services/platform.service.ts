import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PlatformService {
  private readonly baseUrl = environment.apiUrl;
  private readonly platformUrl = `${environment.apiUrl}/api/v1/platform`;

  constructor(private http: HttpClient) {}

  // Platform core
  getPlans() { return this.http.get<any[]>(`${this.platformUrl}/plans`); }
  createPlan(plan: any) { return this.http.post(`${this.platformUrl}/plans`, plan); }
  getTemplates() { return this.http.get<any[]>(`${this.platformUrl}/templates`); }
  createTemplate(template: any) { return this.http.post(`${this.platformUrl}/templates`, template); }
  getCampaigns() { return this.http.get<any[]>(`${this.platformUrl}/campaigns`); }
  createCampaign(campaign: any) { return this.http.post(`${this.platformUrl}/campaigns`, campaign); }
  getNotifications() { return this.http.get<any[]>(`${this.platformUrl}/notifications`); }
  markNotificationRead(id: number) { return this.http.post(`${this.platformUrl}/notifications/${id}/read`, {}); }
  getBranches(orgId?: number) {
    let params = new HttpParams();
    if (orgId) {
      params = params.set('organization_id', String(orgId));
    }
    return this.http.get<any[]>(`${this.platformUrl}/branches`, { params });
  }
  createBranch(branch: any) { return this.http.post(`${this.platformUrl}/branches`, branch); }
  updateBranch(id: number, branch: any) { return this.http.patch(`${this.platformUrl}/branches/${id}`, branch); }
  deleteBranch(id: number) { return this.http.delete(`${this.platformUrl}/branches/${id}`); }
  getBranchAnalytics(orgId: number) { return this.http.get<any>(`${this.baseUrl}/api/v1/organization/${orgId}/branch-analytics`); }
  notifyStaff(orgId: number, payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/organization/${orgId}/notify-staff`, payload); }
  raiseComplaint(payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/organization/raise-complaint`, payload); }
  getReportSummary() { return this.http.get<any>(`${this.platformUrl}/reports/summary`); }

  // Appointments (Staff & Org Admin)
  getAppointments(filters?: { branch_id?: any, date?: string, status?: string }) {
    let params: any = {};
    if (filters?.branch_id && filters.branch_id !== 'ALL') params.branch_id = filters.branch_id;
    if (filters?.date && filters.date !== 'ALL') params.date = filters.date;
    if (filters?.status && filters.status !== 'ALL') params.status = filters.status;
    return this.http.get<any[]>(`${this.baseUrl}/appointments`, { params });
  }
  createAppointment(appointment: any) { return this.http.post<any>(`${this.baseUrl}/appointments`, appointment); }
  updateAppointment(id: number, body: any) { return this.http.patch<any>(`${this.baseUrl}/appointments/${id}`, body); }
  replyAppointment(id: number, payload: { message: string, sender?: string, sender_role?: string }) {
    return this.http.post<any>(`${this.baseUrl}/appointments/${id}/reply`, payload);
  }
  bulkMessageToday(payload: { organization_id: number, message_template?: string, branch_id?: number }) {
    return this.http.post<any>(`${this.baseUrl}/appointments/bulk-message-today`, payload);
  }
  getCustomerHistory(query: { phone?: string, name?: string }) {
    return this.http.get<any>(`${this.baseUrl}/api/v1/customers/history`, { params: query });
  }

  // Services Catalog
  getServices() { return this.http.get<any[]>(`${this.baseUrl}/api/v1/services`); }
  createService(service: any) { return this.http.post(`${this.baseUrl}/api/v1/services`, service); }
  updateService(id: number, service: any) { return this.http.put(`${this.baseUrl}/api/v1/services/${id}`, service); }
  deleteService(id: number) { return this.http.delete(`${this.baseUrl}/api/v1/services/${id}`); }
  importSectorTemplate(sector: string) { return this.http.post<any>(`${this.baseUrl}/api/v1/services/import-sector`, { sector }); }

  // Customer CRM
  getCustomers() { return this.http.get<any[]>(`${this.baseUrl}/api/v1/customers`); }
  createCustomer(customer: any) { return this.http.post(`${this.baseUrl}/api/v1/customers`, customer); }
  getCustomer(id: number) { return this.http.get<any>(`${this.baseUrl}/api/v1/customers/${id}`); }
  updateCustomer(id: number, customer: any) { return this.http.put(`${this.baseUrl}/api/v1/customers/${id}`, customer); }
  deleteCustomer(id: number) { return this.http.delete(`${this.baseUrl}/api/v1/customers/${id}`); }
  getCustomerTimeline(id: number) { return this.http.get<any>(`${this.baseUrl}/api/v1/customers/${id}/timeline`); }

  // WhatsApp Meta Cloud API & Bot Simulator
  getWhatsAppConfig() { return this.http.get<any>(`${this.baseUrl}/api/v1/whatsapp/config`); }
  updateWhatsAppConfig(config: any) { return this.http.post(`${this.baseUrl}/api/v1/whatsapp/config`, config); }
  getWhatsAppLogs() { return this.http.get<any[]>(`${this.baseUrl}/api/v1/whatsapp/logs`); }
  sendWhatsAppMessage(payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/whatsapp/send`, payload); }
  simulateWhatsAppChat(payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/whatsapp/simulate-chat`, payload); }

  // Payments & Razorpay
  getPaymentConfig() { return this.http.get<any>(`${this.baseUrl}/api/v1/payments/config`); }
  updatePaymentConfig(config: any) { return this.http.post(`${this.baseUrl}/api/v1/payments/config`, config); }
  createPaymentOrder(order: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/payments/create-order`, order); }
  verifyPayment(payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/payments/verify`, payload); }

  // Audit Logs
  getAuditLogs(query?: any) { return this.http.get<any[]>(`${this.baseUrl}/api/v1/audit-logs`, { params: query || {} }); }

  // Environment & External Subscription Config
  getEnvConfig() { return this.http.get<any>(`${this.baseUrl}/api/v1/platform/env-config`); }
  updateEnvConfig(config: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/platform/env-config`, config); }

  // Staff & RBAC
  getStaff() { return this.http.get<any[]>(`${this.baseUrl}/api/v1/organization/staff`); }
  createStaff(staff: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/organization/staff`, staff); }
  updateStaff(id: number, staff: any) { return this.http.put<any>(`${this.baseUrl}/api/v1/organization/staff/${id}`, staff); }
  deleteStaff(id: number) { return this.http.delete<any>(`${this.baseUrl}/api/v1/organization/staff/${id}`); }

  // Secrets Diagnostics & AI Triage
  getSecretsStatus() { return this.http.get<any>(`${this.baseUrl}/api/v1/platform/secrets-status`); }
  getAiTriage(payload: any) { return this.http.post<any>(`${this.baseUrl}/api/v1/ai/triage`, payload); }
}
