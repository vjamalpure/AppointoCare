import { Component, OnInit } from '@angular/core';
import { IndustryService, SectorAddon, IndustryRecordItem } from '../../services/industry.service';
import { AuthService } from '../../auth/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-industry-suite',
  templateUrl: './industry-suite.component.html',
  styleUrls: ['./industry-suite.component.scss']
})
export class IndustrySuiteComponent implements OnInit {
  sector = 'Healthcare';
  terms: any;
  config: any;
  addons: SectorAddon[] = [];
  records: IndustryRecordItem[] = [];
  benchmarks: any = null;

  activeTab: 'tool' | 'queue' | 'addons' | 'records' = 'tool';
  loading = false;
  savingRecord = false;

  // Live Queue & Token Board State
  queueTokens: any[] = [];
  loadingQueue = false;
  showTokenModal = false;
  newToken: any = {
    client_name: '',
    phone: '',
    service: 'General Consultation',
    priority: 'Standard',
    assigned_staff: 'Next Available Specialist',
    notes: ''
  };

  // Actuarial & Financial Calculators
  insuranceCalcInput = {
    age: 32,
    sum_assured: 1000000,
    is_smoker: false,
    policy_term: 25,
    riders: ['critical_illness']
  };
  insuranceResult: any = null;
  calculatingInsurance = false;

  realEstateCalcInput = {
    purchase_price: 1250000,
    monthly_rent: 7500,
    annual_expenses: 18000
  };
  realEstateResult: any = null;
  calculatingRealEstate = false;

  // Generic tool form state adapting to current sector
  toolForm: any = {
    title: '',
    client_name: '',
    // Healthcare
    diagnosis: 'Acute Seasonal Bronchitis & Pharyngitis',
    vitals_bp: '120/80',
    vitals_pulse: '74 bpm',
    vitals_temp: '98.4 °F',
    vitals_spo2: '99%',
    medications: [
      { name: 'Amoxicillin 500mg', dosage: '1 tablet 3x daily', duration: '7 days', instructions: 'Take after meals' },
      { name: 'Paracetamol 650mg', dosage: '1 tablet PRN', duration: '3 days', instructions: 'For fever or body pain' }
    ],
    // Salon
    treatment_room: 'Suite A - Aromatherapy Sanctuary',
    selected_upsells: ['Herbal Foot Soak', 'Collagen Eye Mask'],
    hair_skin_formula: '7.1 Ash Blonde + 20 Vol (1:1.5 ratio), Lavender oil 4 drops',
    // Finance
    investable_net_worth: '₹ 1,25,00,000',
    risk_tolerance: 'Moderate Growth',
    equity_pct: 65,
    fixed_income_pct: 25,
    cash_alternatives_pct: 10,
    fiduciary_disclosures_accepted: true,
    // Retail
    fitting_suite: 'Platinum VIP Lounge',
    wardrobe_measurements: 'Chest: 40", Waist: 32", Inseam: 32", Shoe: 10 US',
    curated_lookbook_items: 'Bespoke Silk Tuxedo, Hand-stitched Leather Loafers',
    // Insurance
    policy_type: 'Comprehensive Term Life + Critical Illness',
    sum_assured: '₹ 1,00,00,000',
    tobacco_use: 'Non-Smoker',
    annual_premium_estimate: '₹ 28,400 / year',
    // Education
    target_major: 'Computer Science & AI',
    student_gpa: '3.92 / 4.0',
    standardized_score: 'SAT 1520 / TOEFL 112',
    reach_universities: 'Stanford University, MIT',
    match_universities: 'Georgia Tech, UC San Diego',
    safety_universities: 'Purdue University, Ohio State',
    // Legal
    matter_title: 'Cross-Border SaaS Master Services Agreement',
    adverse_parties_checked: 'Verified - No conflict detected',
    retainer_hours_deposited: '15.0 Hours',
    billable_rate: '₹ 12,500 / hour',
    // Real Estate
    property_wishlist: '3-BHK Penthouse with Skyline Terrace',
    budget_range: '₹ 1.8 Cr - ₹ 2.5 Cr',
    tour_stops: [
      { address: '750 Lexington Ave, Penthouse 40', time: '10:30 AM', lockbox: '8841' },
      { address: '420 Marina Blvd, Loft 12', time: '12:00 PM', lockbox: '9120' }
    ],
    // Enterprise
    sow_deliverable: 'Phase 2: Multi-Region Microservices Migration & Zero-Trust Audit',
    sla_tier: 'Enterprise Platinum (15-min SLA)',
    architecture_framework: 'AWS Well-Architected & SOC2 Type II Certified'
  };

  selectedRecord: IndustryRecordItem | null = null;

  constructor(
    public industryService: IndustryService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.sector = this.industryService.getSector();
    this.terms = this.industryService.getTerms(this.sector);
    this.config = this.industryService.getConfig(this.sector);
    this.initToolDefaults();
    this.loadData();
    this.loadQueue();
    if (this.sector === 'Insurance') {
      this.runInsuranceCalc();
    } else if (this.sector === 'Real Estate') {
      this.runRealEstateCalc();
    }
  }

  initToolDefaults(): void {
    const customer = this.terms?.customerLabel || 'Client';
    this.toolForm.client_name = `Valued ${customer}`;
    this.toolForm.title = `${this.sector} ${this.getDefaultToolName()}`;
  }

  getDefaultToolName(): string {
    switch (this.sector) {
      case 'Healthcare': return 'Clinical E-Prescription & Vitals';
      case 'Salon': return 'Suite Allocation & Formula Consultation';
      case 'Finance': return 'Accredited KYC & Asset Allocation';
      case 'Retail': return 'VIP Sizing & Fitting Suite Profile';
      case 'Insurance': return 'Underwriting Risk & Policy Dossier';
      case 'Education': return 'University Admissions Roadmap';
      case 'Consultancy': return 'Conflict Clearance & Retainer Ledger';
      case 'Real Estate': return 'Property Tour Itinerary';
      case 'Professional Services': return 'SOW Deliverables & Architecture Audit';
      default: return 'Specialized Sector Record';
    }
  }

  getQueueTitle(): string {
    switch (this.sector) {
      case 'Healthcare': return 'Live Clinical OPD & Emergency Queue';
      case 'Salon': return 'Stylist Stations & Treatment Room Floor';
      case 'Finance': return 'Client Wealth Advisory & KYC Consultation Queue';
      case 'Retail': return 'VIP Fitting Lounge & Styling Concierge';
      case 'Real Estate': return 'Today\'s Scheduled Property Showings & Site Visits';
      default: return 'Live Service Queue & Client Waitlist';
    }
  }

  getQueueSubtitle(): string {
    switch (this.sector) {
      case 'Healthcare': return 'Live token board for patient arrival, triage status, and consultation room advance (Practo Ray / Apollo benchmark).';
      case 'Salon': return 'Real-time stylist chair and treatment room occupancy manager (Fresha / Zenoti benchmark).';
      case 'Finance': return 'High-net-worth client arrival tracking and portfolio briefing room dispatch.';
      case 'Retail': return 'Private dressing room suite concierge and personal shopper assignments.';
      case 'Real Estate': return 'Sequenced property tour schedule, attendee arrivals, and lockbox checklist.';
      default: return 'Token calling board and real-time floor occupancy tracker.';
    }
  }

  loadData(): void {
    this.loading = true;
    this.industryService.getAddons().subscribe({
      next: (res) => {
        this.addons = res.addons || [];
      }
    });

    this.industryService.getRecords().subscribe({
      next: (recs) => {
        this.records = recs || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });

    this.industryService.getBenchmarks().subscribe({
      next: (b) => {
        this.benchmarks = b.benchmarks || null;
      }
    });
  }

  // --- Live Queue Actions ---

  loadQueue(): void {
    this.loadingQueue = true;
    this.industryService.getQueue().subscribe({
      next: (tokens) => {
        this.queueTokens = tokens || [];
        this.loadingQueue = false;
      },
      error: () => {
        this.loadingQueue = false;
      }
    });
  }

  advanceToken(token: any, newStatus: string): void {
    this.industryService.advanceQueue(token.id, newStatus).subscribe({
      next: () => {
        token.status = newStatus;
        if (token.data) token.data.queue_status = newStatus;
        this.snackBar.open(`Token status updated to '${newStatus}'`, 'OK', { duration: 2000 });
      },
      error: () => {
        this.snackBar.open('Failed to advance token', 'Dismiss', { duration: 2000 });
      }
    });
  }

  issueToken(): void {
    if (!this.newToken.client_name?.trim()) {
      this.snackBar.open('Please enter client/patient name', 'Dismiss', { duration: 2000 });
      return;
    }

    this.industryService.createQueueToken(this.newToken).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg || 'Token issued successfully', 'OK', { duration: 2500 });
        this.showTokenModal = false;
        this.newToken = { client_name: '', phone: '', service: 'General Consultation', priority: 'Standard', assigned_staff: 'Next Available Specialist', notes: '' };
        this.loadQueue();
      },
      error: () => {
        this.snackBar.open('Failed to issue queue token', 'Dismiss', { duration: 2500 });
      }
    });
  }

  deleteToken(tokenId: number, event?: Event): void {
    if (event) event.stopPropagation();
    if (confirm('Dismiss this token from the active queue?')) {
      this.industryService.deleteQueueToken(tokenId).subscribe({
        next: () => {
          this.snackBar.open('Token dismissed', 'OK', { duration: 2000 });
          this.queueTokens = this.queueTokens.filter(t => t.id !== tokenId);
        }
      });
    }
  }

  // --- Calculators ---

  runInsuranceCalc(): void {
    this.calculatingInsurance = true;
    this.industryService.calculateInsurancePremium(this.insuranceCalcInput).subscribe({
      next: (res) => {
        this.insuranceResult = res;
        this.toolForm.annual_premium_estimate = `₹ ${res.annual_premium.toLocaleString('en-IN')} / year (₹ ${res.monthly_premium.toLocaleString('en-IN')}/mo)`;
        this.calculatingInsurance = false;
      },
      error: () => {
        this.calculatingInsurance = false;
      }
    });
  }

  runRealEstateCalc(): void {
    this.calculatingRealEstate = true;
    this.industryService.calculateRealEstateRoi(this.realEstateCalcInput).subscribe({
      next: (res) => {
        this.realEstateResult = res;
        this.calculatingRealEstate = false;
      },
      error: () => {
        this.calculatingRealEstate = false;
      }
    });
  }

  // --- Add-on & Record Actions ---

  toggleAddon(addon: SectorAddon): void {
    const nextState = !addon.enabled;
    this.industryService.toggleAddon(addon.id, nextState).subscribe({
      next: () => {
        addon.enabled = nextState;
        this.snackBar.open(`Add-on '${addon.name}' is now ${nextState ? 'Active' : 'Disabled'}`, 'OK', { duration: 2500 });
      },
      error: () => {
        this.snackBar.open('Failed to update addon state', 'Close', { duration: 2500 });
      }
    });
  }

  saveCurrentToolRecord(): void {
    this.savingRecord = true;
    const payload: IndustryRecordItem = {
      sector: this.sector,
      record_type: this.getRecordTypeForSector(),
      title: `${this.toolForm.client_name} — ${this.getDefaultToolName()}`,
      data: { ...this.toolForm },
      status: 'Active'
    };

    this.industryService.createRecord(payload).subscribe({
      next: (res) => {
        this.savingRecord = false;
        this.snackBar.open(`Specialized record created: ${res.msg || 'Success'}`, 'OK', { duration: 3000 });
        this.activeTab = 'records';
        this.loadData();
      },
      error: () => {
        this.savingRecord = false;
        this.snackBar.open('Failed to save specialized record', 'Close', { duration: 3000 });
      }
    });
  }

  deleteRecord(id?: number): void {
    if (!id) return;
    if (confirm('Delete this specialized industry record?')) {
      this.industryService.deleteRecord(id).subscribe({
        next: () => {
          this.snackBar.open('Record deleted', 'OK', { duration: 2000 });
          this.records = this.records.filter(r => r.id !== id);
        }
      });
    }
  }

  inspectRecord(rec: IndustryRecordItem): void {
    this.selectedRecord = rec;
  }

  closeInspection(): void {
    this.selectedRecord = null;
  }

  getFormattedAttributes(data: any): { label: string; value: string }[] {
    if (!data) return [];
    const ignored = ['medications', 'tour_stops', 'curated_garments', 'phase_milestones'];
    const attrs: { label: string; value: string }[] = [];
    for (const key of Object.keys(data)) {
      if (ignored.includes(key)) continue;
      const val = data[key];
      if (val === undefined || val === null || val === '') continue;
      const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const formattedVal = typeof val === 'object' ? JSON.stringify(val, null, 2) : String(val);
      attrs.push({ label: formattedKey, value: formattedVal });
    }
    return attrs;
  }

  printDossier(): void {
    window.print();
  }

  getRecordTypeForSector(): string {
    switch (this.sector) {
      case 'Healthcare': return 'prescription';
      case 'Salon': return 'room_allocation';
      case 'Finance': return 'kyc_profile';
      case 'Retail': return 'fitting_card';
      case 'Insurance': return 'claim_file';
      case 'Education': return 'student_milestone';
      case 'Consultancy': return 'billable_retainer';
      case 'Real Estate': return 'tour_itinerary';
      default: return 'sow_milestone';
    }
  }

  addMedicine(): void {
    this.toolForm.medications.push({
      name: 'New Medication',
      dosage: '1 tablet',
      duration: '5 days',
      instructions: 'With water'
    });
  }

  removeMedicine(index: number): void {
    this.toolForm.medications.splice(index, 1);
  }

  addTourStop(): void {
    this.toolForm.tour_stops.push({
      address: 'New Property Address',
      time: '02:00 PM',
      lockbox: '1234'
    });
  }

  removeTourStop(index: number): void {
    this.toolForm.tour_stops.splice(index, 1);
  }
}
