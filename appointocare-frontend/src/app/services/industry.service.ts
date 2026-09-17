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
}

