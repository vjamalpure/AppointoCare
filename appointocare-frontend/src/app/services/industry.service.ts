import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  IndustryConfig,
  getIndustryConfig,
  getIndustryTerms,
  getIndustryCustomFields,
  getIndustryInfoMessages,
  getIndustryWhatsAppDefaults,
  ALL_INDUSTRY_TEMPLATES
} from '../utils/industry.config';
import { IndustryCustomFieldDef, IndustryInfoMessagePreset } from '../utils/industry-custom-data';

export interface SectorAddon {
  id: string;
  name: string;
  benchmark_source?: string;
  benchmark?: string;
  category: string;
  description: string;
  is_default: boolean;
  icon: string;
  enabled?: boolean;
  features?: string[];
}

export interface IndustryRecordItem {
  id?: number;
  organization_id?: number;
  appointment_id?: number | null;
  customer_id?: number | null;
  sector: string;
  record_type: string;
  title: string;
  data: any;
  status?: string;
  created_by_user?: string;
  created_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class IndustryService {
  private readonly baseUrl = environment.apiUrl;
  private readonly SECTOR_KEY = 'appointocare_org_sector';
  private currentSectorSubject = new BehaviorSubject<string>(this.loadInitialSector());
  public currentSector$: Observable<string> = this.currentSectorSubject.asObservable();

  constructor(private http: HttpClient) {}

  private loadInitialSector(): string {
    return localStorage.getItem(this.SECTOR_KEY) || sessionStorage.getItem(this.SECTOR_KEY) || 'Healthcare';
  }

  public setSector(sector: string, persist = true): void {
    if (!sector) return;
    if (persist) {
      localStorage.setItem(this.SECTOR_KEY, sector);
    }
    this.currentSectorSubject.next(sector);
  }

  public getSector(): string {
    return this.currentSectorSubject.value;
  }

  public getConfig(sector?: string | null): IndustryConfig {
    return getIndustryConfig(sector || this.getSector());
  }

  public getTerms(sector?: string | null) {
    return getIndustryTerms(sector || this.getSector());
  }

  public getCustomFields(sector?: string | null): IndustryCustomFieldDef[] {
    return getIndustryCustomFields(sector || this.getSector());
  }

  public getInfoMessages(sector?: string | null): IndustryInfoMessagePreset[] {
    return getIndustryInfoMessages(sector || this.getSector());
  }

  public getWhatsAppDefaults(sector?: string | null) {
    return getIndustryWhatsAppDefaults(sector || this.getSector());
  }

  public getAllTemplates(): IndustryConfig[] {
    return ALL_INDUSTRY_TEMPLATES;
  }

  // --- Industry Suite Backend API Integrations ---

  public getAddons(orgId?: number, allSectors = false): Observable<any> {
    let params = new HttpParams();
    if (orgId) {
      params = params.set('organization_id', String(orgId));
    }
    if (allSectors) {
      params = params.set('all_sectors', 'true');
    }
    return this.http.get<any>(
      `${this.baseUrl}/api/v1/industry-suite/addons`,
      { params }
    );
  }

  public toggleAddon(addonId: string, enabled: boolean, orgId?: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/addons/toggle`, {
      addon_id: addonId,
      enabled,
      organization_id: orgId
    });
  }

  public getRecords(filters?: { record_type?: string; appointment_id?: number; customer_id?: number; organization_id?: any; all?: boolean; sector?: string }): Observable<IndustryRecordItem[]> {
    let params = new HttpParams();
    if (filters?.all) params = params.set('all', 'true');
    if (filters?.organization_id) params = params.set('organization_id', String(filters.organization_id));
    if (filters?.sector) params = params.set('sector', filters.sector);
    if (filters?.record_type) params = params.set('record_type', filters.record_type);
    if (filters?.appointment_id) params = params.set('appointment_id', String(filters.appointment_id));
    if (filters?.customer_id) params = params.set('customer_id', String(filters.customer_id));

    return this.http.get<IndustryRecordItem[]>(`${this.baseUrl}/api/v1/industry-suite/records`, { params });
  }

  public createRecord(payload: IndustryRecordItem): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/records`, payload);
  }

  public deleteRecord(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/api/v1/industry-suite/records/${id}`);
  }

  public downloadRecordPdf(id: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/api/v1/industry-suite/records/${id}/download-pdf`, {
      responseType: 'blob'
    });
  }

  public getBenchmarks(all = false, sector?: string): Observable<any> {
    let params = new HttpParams();
    if (all) params = params.set('all', 'true');
    if (sector) params = params.set('sector', sector);
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/benchmarks`, { params });
  }

  public getSectorStats(orgId?: number): Observable<any> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/stats`, { params });
  }

  // --- Live Queue & Token Board APIs ---

  public getQueue(orgId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/industry-suite/queue`, { params });
  }

  public advanceQueue(recordId: number, status: string, orgId?: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/queue/advance`, {
      record_id: recordId,
      status,
      organization_id: orgId
    });
  }

  public createQueueToken(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/queue/create`, payload);
  }

  public deleteQueueToken(recordId: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/api/v1/industry-suite/queue/${recordId}`);
  }

  // --- Specialized Actuarial & Financial Calculators ---

  public calculateInsurancePremium(payload: { age: number; sum_assured: number; is_smoker: boolean; policy_term?: number; riders?: string[] }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/calculate-insurance-premium`, payload);
  }

  public calculateRealEstateRoi(payload: { purchase_price: number; monthly_rent: number; annual_expenses?: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/calculate-real-estate-roi`, payload);
  }

  // --- Granular Workflow Machine APIs ---

  public redeemSessionCredit(recordId: number, payload: { sessions_to_redeem: number; service_name?: string; staff_name?: string; notes?: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/records/${recordId}/redeem-session-credit`, payload);
  }

  public logBillableTime(recordId: number, payload: { hours: number; hourly_rate: number; activity_description: string; lawyer_name?: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/records/${recordId}/log-billable-time`, payload);
  }

  public transitionClaimStatus(recordId: number, payload: { new_status: string; adjuster_notes?: string; approved_amount?: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/records/${recordId}/transition-claim-status`, payload);
  }

  public updateAlterationStage(recordId: number, payload: { stage: string; tailor_notes?: string; fitting_suite?: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/records/${recordId}/update-alteration-stage`, payload);
  }

  public scheduleFollowupAppointment(appointmentId: number, payload: { followup_date: string; service_name?: string; staff_name?: string; notes?: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/appointments/${appointmentId}/schedule-followup`, payload);
  }

  public generateRebalancePlan(payload: { portfolio_value: number; current_weights: any; target_weights: any; fee_bps?: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/generate-rebalance-plan`, payload);
  }

  public getRecordLedgerAudit(recordId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/records/${recordId}/ledger-audit`);
  }

  // --- Dynamic Custom Fields APIs ---

  public getCustomFieldDefinitions(orgId?: number): Observable<any> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any>(`${this.baseUrl}/api/v1/custom-fields/definitions`, { params });
  }

  public createCustomFieldDefinition(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/custom-fields/definitions`, payload);
  }

  // --- Configurable Workflow State Machine APIs ---

  public getWorkflowDefinitions(orgId?: number): Observable<any> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any>(`${this.baseUrl}/api/v1/workflows/definitions`, { params });
  }

  public executeWorkflowTransition(recordId: number, payload: { target_status: string; comment?: string; additional_data?: any }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/workflows/records/${recordId}/transition`, payload);
  }

  public getWorkflowHistory(recordId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/workflows/records/${recordId}/history`);
  }

  // --- Cross-Industry Operational Analytics & Export ---

  public getOperationalKpis(orgId?: number): Observable<any> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any>(`${this.baseUrl}/api/v1/analytics/operational-kpis`, { params });
  }

  public getAnalyticsExportUrl(format = 'xlsx', orgId?: number): string {
    const orgQuery = orgId ? `&organization_id=${orgId}` : '';
    return `${this.baseUrl}/api/v1/analytics/export?format=${format}${orgQuery}`;
  }

  // --- Advanced Automation Rules APIs ---

  public getAutomationRules(orgId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (orgId) params = params.set('organization_id', String(orgId));
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/automations/rules`, { params });
  }

  public createOrToggleAutomationRule(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/automations/rules`, payload);
  }

  public triggerAutomationRule(ruleId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/automations/rules/${ruleId}/trigger`, {});
  }

  // --- 9-Industry Competitive Feature Packs ---

  // 1. Healthcare
  public getHealthcareTimeline(customerId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/healthcare/patient/${customerId}/timeline`);
  }

  public getClinicalTemplates(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/healthcare/clinical-templates`);
  }

  public getHealthcareFhirBundle(customerId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/healthcare/patient/${customerId}/fhir-bundle`);
  }

  // 2. Salon & Wellness
  public enrollSalonMembership(payload: { customer_id: number; tier: string; fee_paid?: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/salon/memberships/enroll`, payload);
  }

  public getSalonLoyalty(customerId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/salon/customers/${customerId}/loyalty`);
  }

  public logSalonConsumables(recordId: number, items: any[]): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/salon/records/${recordId}/log-consumables`, { items });
  }

  // 3. Finance & Wealth
  public evaluateFinanceRiskProfile(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/finance/evaluate-risk-profile`, payload);
  }

  public updateFinanceCompliance(recordId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/finance/records/${recordId}/compliance-checklist`, payload);
  }

  // 4. Insurance
  public compareInsuranceQuotes(payload: { age: number; sum_assured: number }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/compare-quotes`, payload);
  }

  public getInsuranceRenewals(days = 60): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/renewals-upcoming?days=${days}`);
  }

  // 5. Retail & Luxury
  public getRetailCatalog(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/retail/catalog`);
  }

  public logRetailStockMovement(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/retail/stock-movement`, payload);
  }

  public createRetailLookbook(customerId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/retail/customers/${customerId}/lookbook`, payload);
  }

  // 6. Education
  public compareEducationUniversities(payload?: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/education/compare-universities`, payload || {});
  }

  public updateEducationVisaChecklist(recordId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/education/records/${recordId}/visa-checklist`, payload);
  }

  // 7. Legal & Consultancy
  public runLegalConflictReview(payload: { adverse_party: string; matter_title?: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/legal/conflict-review`, payload);
  }

  public getLegalRetainerStatement(recordId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/legal/records/${recordId}/retainer-statement`);
  }

  // 8. Real Estate
  public getRealEstateProperties(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/properties`);
  }

  public calculateRealEstateCommission(recordId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/deals/${recordId}/calculate-commission`, payload);
  }

  // 9. Professional Services
  public getResourceUtilization(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/professional-services/resource-utilization`);
  }

  public logSlaEscalation(recordId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/professional-services/records/${recordId}/sla-escalation`, payload);
  }

  // 10. Platform Integration Status Gateway
  public getPlatformIntegrationsStatus(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/platform/integrations/status`);
  }

  // =========================================================================
  // ITERATION 5: SHARED COMMERCIAL WORKBENCH & HEALTHCARE CLINICAL ENGINE
  // =========================================================================

  // Tasks Management
  public getTasks(params?: any): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/tasks`, { params });
  }

  public createTask(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/tasks`, payload);
  }

  public updateTask(taskId: number, payload: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/api/v1/tasks/${taskId}`, payload);
  }

  public escalateTask(taskId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/tasks/${taskId}/escalate`, {});
  }

  public getTaskSummary(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/tasks/summary`);
  }

  // Business Pipelines
  public getPipelines(sector?: string): Observable<any[]> {
    const url = sector ? `${this.baseUrl}/api/v1/pipelines?sector=${encodeURIComponent(sector)}` : `${this.baseUrl}/api/v1/pipelines`;
    return this.http.get<any[]>(url);
  }

  public addPipelineDeal(pipelineId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/pipelines/${pipelineId}/deals`, payload);
  }

  public movePipelineDeal(pipelineId: number, dealId: string, stageId: string): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/api/v1/pipelines/${pipelineId}/deals/${dealId}/move`, { stage_id: stageId });
  }

  // Documents & Electronic Approvals
  public getDocumentVersions(docId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/documents/${docId}/versions`);
  }

  public addDocumentVersion(docId: number, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/documents/${docId}/versions`, payload);
  }

  public auditDocumentDownload(docId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/documents/${docId}/audit-download`, {});
  }

  public createApproval(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/documents/approvals`, payload);
  }

  public getApprovals(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/documents/approvals`);
  }

  // Healthcare Clinical Command Center
  public createClinicalEncounter(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/encounters`, payload);
  }

  public getClinicalEncounter(encounterId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/healthcare/encounters/${encounterId}`);
  }

  public signOffClinicalEncounter(encounterId: number, payload?: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/encounters/${encounterId}/sign-off`, payload || {});
  }

  public getPatientEncounters(patientId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/healthcare/encounters/patient/${patientId}`);
  }

  public addToHealthcareWaitlist(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/waitlist`, payload);
  }

  public getHealthcareWaitlist(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/api/v1/healthcare/waitlist`);
  }

  public promoteHealthcareWaitlist(waitlistId: number, payload?: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/waitlist/${waitlistId}/promote`, payload || {});
  }

  public scheduleResourceRoom(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/resources/schedule`, payload);
  }

  public getResourceAvailability(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/healthcare/resources/availability`);
  }

  public createLabOrder(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/lab-orders`, payload);
  }

  public reviewLabOrder(orderId: number, payload: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/api/v1/healthcare/lab-orders/${orderId}/review`, payload);
  }

  public getLabOrders(status?: string): Observable<any[]> {
    const url = status ? `${this.baseUrl}/api/v1/healthcare/lab-orders?status=${status}` : `${this.baseUrl}/api/v1/healthcare/lab-orders`;
    return this.http.get<any[]>(url);
  }

  public getClinicOperationalDashboard(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/healthcare/operational-dashboard`);
  }

  public issueAbdmConsent(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/abdm/consent`, payload);
  }

  // Customer 360 Timeline & Batch Import
  public getCustomerUnifiedTimeline(customerId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/customers/${customerId}/unified-timeline`);
  }

  public validateCustomerImport(rows: any[]): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/customers/import-validate`, { rows });
  }

  public bulkImportCustomers(records: any[]): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/customers/bulk-import`, { records });
  }

  // Eight Industry Domain Deepening Actions
  public renewSalonMembership(membershipId: string, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/salon/memberships/${membershipId}/renew`, payload);
  }

  public redeemSalonLoyalty(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/salon/loyalty/redeem`, payload);
  }

  public getLowStockConsumables(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/salon/consumables/low-stock`);
  }

  public reviewFinanceSuitability(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/finance/suitability-review`, payload);
  }

  public calculateAdvisoryFees(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/finance/fees/calculate`, payload);
  }

  public convertQuoteToPolicy(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/quote-to-policy`, payload);
  }

  public verifyClaimDocs(claimId: string, payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/claims/${claimId}/verify-docs`, payload);
  }

  public createRetailOrder(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/retail/orders`, payload);
  }

  public getRetailClienteling(customerId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/retail/clienteling/${customerId}`);
  }

  public getRetailStockVisibility(sku: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/retail/stock-visibility?sku=${encodeURIComponent(sku)}`);
  }

  public convertEducationLead(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/education/lead-conversion`, payload);
  }

  public getCounselorWorkload(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/education/counselor-workload`);
  }

  public setupTuitionSchedule(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/education/tuition-schedule`, payload);
  }

  public getLegalLimitationDeadlines(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/legal/limitation-deadlines`);
  }

  public approveLegalTimeEntry(entryId: any, payload: any = {}): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/legal/time-entries/${entryId}/approve`, payload);
  }

  public scheduleRealEstateSiteVisit(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/site-visits`, payload);
  }

  public matchBuyerProperties(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/property-match`, payload);
  }

  public submitTimesheet(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/prof-services/timesheets/submit`, payload);
  }

  public approveTimesheet(timesheetId: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/prof-services/timesheets/${timesheetId}/approve`, {});
  }

  public getProjectProfitability(projectId: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/prof-services/projects/${projectId}/profitability`);
  }

  public downloadEncounterPrescriptionPdf(encounterId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/api/v1/healthcare/encounters/${encounterId}/prescription-pdf`, {
      responseType: 'blob'
    });
  }

  public downloadTransactionInvoicePdf(txnId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/api/v1/transactions/${txnId}/invoice-pdf`, {
      responseType: 'blob'
    });
  }

  public generateCustomerPortalLink(customerId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/customers/${customerId}/portal-link`, {});
  }

  public getSubscriptionLimits(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/platform/organization/subscription-limits`);
  }

  // Competitor Matrix & Leader Gap-Closing API Integrations
  public getClosedLoopCare(patientId: number = 1): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/healthcare/closed-loop-care/${patientId}`);
  }

  public getMedicationRefills(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/healthcare/medications/refills`);
  }

  public approveMedicationRefill(refillId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/healthcare/medications/refills/${refillId}/approve`, {});
  }

  public recoverSalonCancellation(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/salon/recover-cancellation`, payload);
  }

  public getSalonRecoveryOffers(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/salon/recovery-offers`);
  }

  public getRetailInventory(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/inventory`);
  }

  public createRetailInventoryItem(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/inventory`, payload);
  }

  public getPortfolioHealth(customerId: number = 1): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/finance/portfolio-health?customer_id=${customerId}`);
  }

  public getHouseholdViews(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/finance/households`);
  }

  public submitSuitabilityProfile(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/finance/suitability-profile`, payload);
  }

  public getRenewalCommandCenter(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/renewal-command-center`);
  }

  public createInsurancePolicy(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/insurance/policies`, payload);
  }

  public getBespokeOrders(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/retail/bespoke-orders`);
  }

  public createBespokeOrder(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/retail/bespoke-orders`, payload);
  }

  public updateBespokeOrderStage(orderId: number, payload: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/api/v1/industry-suite/retail/bespoke-orders/${orderId}/stage`, payload);
  }

  public getUniversityPrograms(query = ''): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/education/programs?q=${encodeURIComponent(query)}`);
  }

  public evaluateStudentReadiness(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/education/readiness-score`, payload);
  }

  public getLegalMatters(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/legal/matters`);
  }

  public createLegalMatter(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/industry-suite/legal/matters`, payload);
  }

  public getPropertyReservations(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/reservations`);
  }

  public getArchitectureProjects(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/real-estate/architecture-projects`);
  }

  public getProjectMargins(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/professional/project-margins`);
  }

  public getIncidentTickets(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/industry-suite/professional/incidents`);
  }

  public dispatchAutomationEvent(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/api/v1/automation/dispatch-event`, payload);
  }

  public getAutomationLogs(limit = 20): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/v1/automation/logs?limit=${limit}`);
  }
}



