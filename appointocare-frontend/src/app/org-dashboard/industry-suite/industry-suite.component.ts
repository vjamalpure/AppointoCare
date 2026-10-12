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

  // Granular Workflow Machine Actions (Workstream 1)
  actionLoading: { [key: string]: boolean } = {};

  salonCreditInput = {
    sessions: 1,
    service_name: 'Treatment & Spa Session',
    staff_name: 'Lead Specialist',
    notes: 'Package credit redemption requested'
  };

  legalTimeInput = {
    hours: 1.5,
    rate: 12500,
    description: 'Matter contract drafting & clause advisory',
    lawyer_name: 'Lead Advocate'
  };

  insuranceClaimInput = {
    status: 'Under_Review',
    notes: 'Surveyor and clinical documentation under review',
    approved_amount: 0
  };

  retailAlterationInput = {
    stage: 'In_Tailoring',
    notes: 'Hemming and shoulder adjustment in progress',
    fitting_suite: 'VIP Lounge 1'
  };

  healthcareFollowupInput = {
    date: '',
    service: 'Clinical Follow-up Consultation',
    notes: 'Post-treatment recovery review'
  };

  financeRebalanceInput = {
    portfolio_value: 500000,
    fee_bps: 10
  };
  financeRebalanceResult: any = null;

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

  // --- Workstream 1: Dedicated Granular Workflow Actions ---

  executeRedeemCredit(record: IndustryRecordItem): void {
    if (!record?.id) return;
    this.actionLoading['redeem'] = true;
    this.industryService.redeemSessionCredit(record.id, {
      sessions_to_redeem: this.salonCreditInput.sessions,
      service_name: this.salonCreditInput.service_name,
      staff_name: this.salonCreditInput.staff_name,
      notes: this.salonCreditInput.notes
    }).subscribe({
      next: (res) => {
        this.actionLoading['redeem'] = false;
        this.snackBar.open(`Redeemed ${res.sessions_redeemed} credit(s). Remaining: ${res.remaining_credits}`, 'OK', { duration: 3500 });
        if (record.data) {
          record.data.remaining_sessions = res.remaining_credits;
        }
        this.loadData();
      },
      error: (err) => {
        this.actionLoading['redeem'] = false;
        const msg = err.error?.msg || 'Failed to redeem credit';
        this.snackBar.open(msg, 'Dismiss', { duration: 3500 });
      }
    });
  }

  executeLogBillableTime(record: IndustryRecordItem): void {
    if (!record?.id) return;
    this.actionLoading['time'] = true;
    this.industryService.logBillableTime(record.id, {
      hours: this.legalTimeInput.hours,
      hourly_rate: this.legalTimeInput.rate,
      activity_description: this.legalTimeInput.description,
      lawyer_name: this.legalTimeInput.lawyer_name
    }).subscribe({
      next: (res) => {
        this.actionLoading['time'] = false;
        this.snackBar.open(`Logged ${res.hours_logged}h (₹${res.billable_amount}). Retainer remaining: ${res.retainer_hours_remaining}h`, 'OK', { duration: 3500 });
        if (record.data) {
          record.data.retainer_hours_remaining = res.retainer_hours_remaining;
          record.data.retainer_depleted_alert = res.retainer_depleted_alert;
        }
        this.loadData();
      },
      error: (err) => {
        this.actionLoading['time'] = false;
        this.snackBar.open(err.error?.msg || 'Failed to log billable time', 'Dismiss', { duration: 3500 });
      }
    });
  }

  executeTransitionClaim(record: IndustryRecordItem): void {
    if (!record?.id) return;
    this.actionLoading['claim'] = true;
    this.industryService.transitionClaimStatus(record.id, {
      new_status: this.insuranceClaimInput.status,
      adjuster_notes: this.insuranceClaimInput.notes,
      approved_amount: this.insuranceClaimInput.approved_amount
    }).subscribe({
      next: (res) => {
        this.actionLoading['claim'] = false;
        this.snackBar.open(`Claim #${record.id} status transitioned to: ${res.current_status}`, 'OK', { duration: 3500 });
        record.status = res.current_status;
        this.loadData();
      },
      error: (err) => {
        this.actionLoading['claim'] = false;
        this.snackBar.open(err.error?.msg || 'Failed to transition claim', 'Dismiss', { duration: 3500 });
      }
    });
  }

  executeUpdateAlteration(record: IndustryRecordItem): void {
    if (!record?.id) return;
    this.actionLoading['alteration'] = true;
    this.industryService.updateAlterationStage(record.id, {
      stage: this.retailAlterationInput.stage,
      tailor_notes: this.retailAlterationInput.notes,
      fitting_suite: this.retailAlterationInput.fitting_suite
    }).subscribe({
      next: (res) => {
        this.actionLoading['alteration'] = false;
        const note = res.ready_for_fitting ? ' (Ready notification queued)' : '';
        this.snackBar.open(`Alteration stage updated to: ${res.current_stage}${note}`, 'OK', { duration: 3500 });
        record.status = res.current_stage;
        this.loadData();
      },
      error: (err) => {
        this.actionLoading['alteration'] = false;
        this.snackBar.open(err.error?.msg || 'Failed to update alteration', 'Dismiss', { duration: 3500 });
      }
    });
  }

  executeScheduleFollowup(appointmentId?: number | null): void {
    const targetId = appointmentId || this.selectedRecord?.appointment_id;
    if (!targetId) {
      this.snackBar.open('No appointment bound to this record for follow-up scheduling', 'Dismiss', { duration: 3000 });
      return;
    }
    const targetDate = this.healthcareFollowupInput.date || new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0] + 'T10:00:00';
    this.actionLoading['followup'] = true;
    this.industryService.scheduleFollowupAppointment(targetId, {
      followup_date: targetDate,
      service_name: this.healthcareFollowupInput.service,
      notes: this.healthcareFollowupInput.notes
    }).subscribe({
      next: (res) => {
        this.actionLoading['followup'] = false;
        this.snackBar.open(`Follow-up appointment #${res.followup_appointment_id} scheduled for ${res.customer_name}`, 'OK', { duration: 3500 });
      },
      error: (err) => {
        this.actionLoading['followup'] = false;
        this.snackBar.open(err.error?.msg || 'Failed to schedule follow-up', 'Dismiss', { duration: 3500 });
      }
    });
  }

  executeGenerateRebalancePlan(): void {
    this.actionLoading['rebalance'] = true;
    const currentWeights = {
      equity: Number(this.toolForm.equity_pct || 65),
      debt: Number(this.toolForm.fixed_income_pct || 25),
      cash: Number(this.toolForm.cash_alternatives_pct || 10)
    };
    const targetWeights = {
      equity: 50,
      debt: 40,
      cash: 10
    };
    this.industryService.generateRebalancePlan({
      portfolio_value: this.financeRebalanceInput.portfolio_value,
      current_weights: currentWeights,
      target_weights: targetWeights,
      fee_bps: this.financeRebalanceInput.fee_bps
    }).subscribe({
      next: (res) => {
        this.actionLoading['rebalance'] = false;
        this.financeRebalanceResult = res;
        this.snackBar.open(`Rebalance plan computed: ₹${res.total_turnover.toLocaleString('en-IN')} turnover`, 'OK', { duration: 3500 });
      },
      error: (err) => {
        this.actionLoading['rebalance'] = false;
        this.snackBar.open(err.error?.msg || 'Failed to compute rebalancing plan', 'Dismiss', { duration: 3500 });
      }
    });
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

  downloadRecordPdf(rec: any): void {
    if (!rec?.id) return;
    this.industryService.downloadRecordPdf(rec.id).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${rec.record_type || 'record'}_${rec.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        this.snackBar.open('PDF downloaded successfully', 'OK', { duration: 2500 });
      },
      error: () => {
        this.snackBar.open('Failed to generate PDF document', 'Dismiss', { duration: 3000 });
      }
    });
  }
}
