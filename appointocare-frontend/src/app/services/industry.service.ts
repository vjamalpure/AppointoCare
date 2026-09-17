import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
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

@Injectable({
  providedIn: 'root'
})
export class IndustryService {
  private readonly SECTOR_KEY = 'appointocare_org_sector';
  private currentSectorSubject = new BehaviorSubject<string>(this.loadInitialSector());
  public currentSector$: Observable<string> = this.currentSectorSubject.asObservable();

  constructor() {}

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
}
