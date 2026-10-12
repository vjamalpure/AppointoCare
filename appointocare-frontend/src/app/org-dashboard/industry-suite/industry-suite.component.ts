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

  activeTab: 'tool' | 'queue' | 'addons' | 'records' | 'analytics' | 'workflows' | 'intelligence' | 'command_center' = 'tool';
  loading = false;
  savingRecord = false;

  // Enterprise Capabilities (Iteration 4)
  customFieldDefinitions: any[] = [];
  workflowDef: any = null;
  recordHistory: any[] = [];
  operationalKpis: any = null;
  automationRules: any[] = [];
  transitionComment = '';
  isTransitioning = false;

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

    this.loadCustomFields();
    this.loadWorkflowDefinitions();
    this.loadOperationalKpis();
    this.loadAutomationRules();
  }

  loadCustomFields(): void {
    this.industryService.getCustomFieldDefinitions().subscribe({
      next: (res) => {
        this.customFieldDefinitions = res.definitions || [];
      }
    });
  }

  loadWorkflowDefinitions(): void {
    this.industryService.getWorkflowDefinitions().subscribe({
      next: (res) => {
        this.workflowDef = res.workflow || null;
      }
    });
  }

  loadOperationalKpis(): void {
    this.industryService.getOperationalKpis().subscribe({
      next: (res) => {
        this.operationalKpis = res || null;
      }
    });
  }

  loadAutomationRules(): void {
    this.industryService.getAutomationRules().subscribe({
      next: (rules) => {
        this.automationRules = rules || [];
      }
    });
  }

  loadRecordHistory(recordId?: number): void {
    if (!recordId) return;
    this.industryService.getWorkflowHistory(recordId).subscribe({
      next: (res) => {
        this.recordHistory = res.history || [];
      }
    });
  }

  executeTransition(record: IndustryRecordItem, targetStatus: string): void {
    if (!record?.id) return;
    this.isTransitioning = true;
    this.industryService.executeWorkflowTransition(record.id, {
      target_status: targetStatus,
      comment: this.transitionComment
    }).subscribe({
      next: (res) => {
        this.isTransitioning = false;
        this.transitionComment = '';
        this.snackBar.open(`Shifted status to '${targetStatus}'`, 'OK', { duration: 3000 });
        record.status = targetStatus;
        this.loadRecordHistory(record.id);
        this.loadData();
      },
      error: (err) => {
        this.isTransitioning = false;
        const msg = err.error?.msg || 'Transition failed';
        this.snackBar.open(msg, 'Close', { duration: 4000 });
      }
    });
  }

  triggerAutomation(ruleId: number): void {
    this.industryService.triggerAutomationRule(ruleId).subscribe({
      next: (res) => {
        this.snackBar.open(`Automation simulated: ${res.rule_name}`, 'OK', { duration: 3000 });
        this.loadAutomationRules();
      }
    });
  }

  toggleAutomation(rule: any): void {
    this.industryService.createOrToggleAutomationRule({
      id: rule.id,
      is_active: !rule.is_active
    }).subscribe({
      next: () => {
        rule.is_active = !rule.is_active;
        this.snackBar.open(`Rule is now ${rule.is_active ? 'Active' : 'Paused'}`, 'OK', { duration: 2500 });
      }
    });
  }

  downloadAnalyticsReport(fmt = 'xlsx'): void {
    const url = this.industryService.getAnalyticsExportUrl(fmt);
    window.open(url, '_blank');
    this.snackBar.open(`Downloading ${fmt.toUpperCase()} operational analytics report...`, 'OK', { duration: 3000 });
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
    if (rec?.id) {
      this.loadRecordHistory(rec.id);
    }
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

  // --- 9-Industry Intelligence & Feature Pack Actions ---

  public activeFeatureModal: string | null = null;
  public patientTimeline: any = null;
  public fhirBundleJson: string | null = null;
  public salonLoyaltyData: any = null;
  public riskProfileResult: any = null;
  public insuranceQuotesResult: any = null;
  public insuranceRenewalsList: any[] = [];
  public retailCatalogList: any[] = [];
  public universityComparisonResult: any[] = [];
  public legalConflictResult: any = null;
  public retainerStatementData: any = null;
  public realEstatePropertiesList: any[] = [];
  public resourceUtilizationData: any = null;
  public integrationsStatusData: any = null;

  public loadHealthcareTimeline(customerId: number): void {
    this.industryService.getHealthcareTimeline(customerId).subscribe({
      next: (res) => {
        this.patientTimeline = res;
        this.activeFeatureModal = 'healthcare_timeline';
      },
      error: () => this.snackBar.open('Could not load patient timeline', 'Close', { duration: 3000 })
    });
  }

  public exportFhirBundle(customerId: number): void {
    this.industryService.getHealthcareFhirBundle(customerId).subscribe({
      next: (res) => {
        this.fhirBundleJson = JSON.stringify(res, null, 2);
        this.activeFeatureModal = 'fhir_bundle';
      },
      error: () => this.snackBar.open('FHIR export failed', 'Close', { duration: 3000 })
    });
  }

  public enrollSalonMembership(customerId: number, tier = 'Gold'): void {
    this.industryService.enrollSalonMembership({ customer_id: customerId, tier }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadSalonLoyalty(customerId);
      }
    });
  }

  public loadSalonLoyalty(customerId: number): void {
    this.industryService.getSalonLoyalty(customerId).subscribe({
      next: (res) => {
        this.salonLoyaltyData = res;
        this.activeFeatureModal = 'salon_loyalty';
      }
    });
  }

  public logConsumablesUsage(recordId: number): void {
    const items = [
      { product: 'Professional Moroccan Argan Serum', units: 30, cost: 240 }
    ];
    this.industryService.logSalonConsumables(recordId, items).subscribe({
      next: (res) => {
        this.snackBar.open('Consumable usage logged atomically', 'OK', { duration: 3000 });
        this.loadData();
      }
    });
  }

  public evaluateRiskProfile(lossReaction = 'HOLD', horizon = 7): void {
    this.industryService.evaluateFinanceRiskProfile({
      loss_reaction: lossReaction,
      time_horizon_years: horizon,
      investment_goal: 'GROWTH'
    }).subscribe({
      next: (res) => {
        this.riskProfileResult = res;
        this.activeFeatureModal = 'risk_profile';
      }
    });
  }

  public recordFinanceCompliance(recordId?: number): void {
    const id: number = recordId || (this.records.length && this.records[0].id ? this.records[0].id : 1);
    this.industryService.updateFinanceCompliance(id, {
      kyc_id_verified: true,
      aml_pep_screened: true,
      source_of_wealth_documented: true,
      risk_disclosure_executed: true,
      notes: 'All compliance disclosures completed and countersigned.'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadData();
      }
    });
  }

  public compareInsuranceQuotes(age = 35, sumAssured = 1000000): void {
    this.industryService.compareInsuranceQuotes({ age, sum_assured: sumAssured }).subscribe({
      next: (res) => {
        this.insuranceQuotesResult = res;
        this.activeFeatureModal = 'insurance_quotes';
      }
    });
  }

  public loadInsuranceRenewals(): void {
    this.industryService.getInsuranceRenewals(60).subscribe({
      next: (res) => {
        this.insuranceRenewalsList = res.upcoming_renewals || [];
        this.activeFeatureModal = 'insurance_renewals';
      }
    });
  }

  public loadRetailCatalog(): void {
    this.industryService.getRetailCatalog().subscribe({
      next: (res) => {
        this.retailCatalogList = res.catalog || [];
        this.activeFeatureModal = 'retail_catalog';
      }
    });
  }

  public logRetailStock(sku: string, qty = 5): void {
    this.industryService.logRetailStockMovement({ sku, quantity: qty, movement_type: 'RESTOCK' }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
      }
    });
  }

  public compareEducationUniversities(): void {
    this.industryService.compareEducationUniversities().subscribe({
      next: (res) => {
        this.universityComparisonResult = res.comparison || [];
        this.activeFeatureModal = 'education_comparison';
      }
    });
  }

  public updateVisaChecklist(recordId?: number): void {
    const id: number = recordId || (this.records.length && this.records[0].id ? this.records[0].id : 1);
    this.industryService.updateEducationVisaChecklist(id, {
      cas_or_i20_received: true,
      bank_financial_affidavit: true,
      tb_medical_clearance: true,
      biometrics_appointment: true,
      visa_vignette_issued: true
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadData();
      }
    });
  }

  public runConflictCheck(adverseParty: string): void {
    if (!adverseParty) {
      this.snackBar.open('Please provide adverse party name', 'Close', { duration: 2500 });
      return;
    }
    this.industryService.runLegalConflictReview({ adverse_party: adverseParty }).subscribe({
      next: (res) => {
        this.legalConflictResult = res;
        this.activeFeatureModal = 'legal_conflict';
      }
    });
  }

  public loadRetainerStatement(recordId?: number): void {
    const id: number = recordId || (this.records.length && this.records[0].id ? this.records[0].id : 1);
    this.industryService.getLegalRetainerStatement(id).subscribe({
      next: (res) => {
        this.retainerStatementData = res;
        this.activeFeatureModal = 'retainer_statement';
      }
    });
  }

  public loadRealEstateProperties(): void {
    this.industryService.getRealEstateProperties().subscribe({
      next: (res) => {
        this.realEstatePropertiesList = res.properties || [];
        this.activeFeatureModal = 're_properties';
      }
    });
  }

  public calcDealCommission(recordId?: number): void {
    const id: number = recordId || (this.records.length && this.records[0].id ? this.records[0].id : 1);
    this.industryService.calculateRealEstateCommission(id, {
      sale_price: 15000000,
      commission_rate_pct: 2.0,
      broker_split_pct: 50.0
    }).subscribe({
      next: (res) => {
        this.snackBar.open(`Gross Commission: ₹${res.gross_commission.toLocaleString()} (Listing Agent: ₹${res.listing_agent_share.toLocaleString()})`, 'OK', { duration: 4000 });
      }
    });
  }

  public loadResourceUtilization(): void {
    this.industryService.getResourceUtilization().subscribe({
      next: (res) => {
        this.resourceUtilizationData = res;
        this.activeFeatureModal = 'resource_utilization';
      }
    });
  }

  public logSlaIncident(recordId?: number): void {
    const id: number = recordId || (this.records.length && this.records[0].id ? this.records[0].id : 1);
    this.industryService.logSlaEscalation(id, {
      severity: 'P1 - Critical',
      incident_summary: 'Primary database connection pool exhaustion detected'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadData();
      }
    });
  }

  public integrationList: any[] = [];

  public loadIntegrationsStatus(): void {
    this.industryService.getPlatformIntegrationsStatus().subscribe({
      next: (res) => {
        this.integrationsStatusData = res.integrations || {};
        this.integrationList = Object.values(res.integrations || {});
        this.activeFeatureModal = 'integrations_status';
      }
    });
  }

  // =========================================================================
  // ITERATION 5: CLINICAL COMMAND CENTER & COMMERCIAL WORKBENCH
  // =========================================================================
  public tasksList: any[] = [];
  public taskSummary: any = null;
  public newTaskTitle = '';
  public newTaskPriority = 'Medium';
  public pipelinesList: any[] = [];
  public waitlistItems: any[] = [];
  public labOrdersList: any[] = [];
  public clinicDashboardData: any = null;
  public customerTimelineData: any = null;
  public clinicalEncountersList: any[] = [];
  public roomReservations: any[] = [];
  public importValidationSummary: any = null;
  public newEncounterChiefComplaint = 'Episodic chest tightness and breathlessness on exertion';
  public newEncounterNotes = 'Patient alert, oriented. Vitals stable. Systemic examination normal.';
  public newEncounterRx = 'Telmisartan 40mg OD, Atorvastatin 20mg HS';

  public loadTasks(): void {
    this.industryService.getTasks().subscribe({
      next: (res) => {
        this.tasksList = res || [];
      }
    });
    this.industryService.getTaskSummary().subscribe({
      next: (res) => {
        this.taskSummary = res;
      }
    });
  }

  public handleCreateTask(): void {
    if (!this.newTaskTitle.trim()) {
      this.snackBar.open('Please enter a task title', 'Dismiss', { duration: 3000 });
      return;
    }
    this.industryService.createTask({
      title: this.newTaskTitle,
      priority: this.newTaskPriority,
      assigned_to_name: 'Lead Specialist'
    }).subscribe({
      next: () => {
        this.snackBar.open('Task created successfully', 'OK', { duration: 3000 });
        this.newTaskTitle = '';
        this.loadTasks();
      }
    });
  }

  public handleEscalateTask(taskId: number): void {
    this.industryService.escalateTask(taskId).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadTasks();
      }
    });
  }

  public handleCompleteTask(taskId: number): void {
    this.industryService.updateTask(taskId, { status: 'Completed' }).subscribe({
      next: () => {
        this.snackBar.open('Task marked completed', 'OK', { duration: 3000 });
        this.loadTasks();
      }
    });
  }

  public loadPipelines(): void {
    this.industryService.getPipelines(this.sector).subscribe({
      next: (res) => {
        this.pipelinesList = res || [];
      }
    });
  }

  public handleMoveDeal(pipelineId: number, dealId: string, stageId: string): void {
    this.industryService.movePipelineDeal(pipelineId, dealId, stageId).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadPipelines();
      }
    });
  }

  public loadClinicalCommandCenter(): void {
    this.industryService.getHealthcareWaitlist().subscribe({
      next: (res) => {
        this.waitlistItems = res || [];
      }
    });
    this.industryService.getLabOrders().subscribe({
      next: (res) => {
        this.labOrdersList = res || [];
      }
    });
    this.industryService.getClinicOperationalDashboard().subscribe({
      next: (res) => {
        this.clinicDashboardData = res;
      }
    });
    this.industryService.getResourceAvailability().subscribe({
      next: (res) => {
        this.roomReservations = res.active_reservations || [];
      }
    });
    const patientId = this.records.length && this.records[0].customer_id ? this.records[0].customer_id : 1;
    this.industryService.getPatientEncounters(patientId).subscribe({
      next: (res) => {
        this.clinicalEncountersList = res || [];
      }
    });
  }

  public handleCreateEncounter(): void {
    const patientId = this.records.length && this.records[0].customer_id ? this.records[0].customer_id : 1;
    this.industryService.createClinicalEncounter({
      patient_id: patientId,
      encounter_type: 'Outpatient Consultation',
      practitioner_name: 'Dr. Sarah Jenkins',
      practitioner_reg_no: 'MCI-2018-9410',
      chief_complaints: this.newEncounterChiefComplaint,
      clinical_notes: this.newEncounterNotes,
      vitals: { bp_systolic: 128, bp_diastolic: 82, pulse: 76, temp_f: 98.6, spo2: 99, bmi: 22.8 },
      prescription_data: { rx_number: `RX-${Date.now()}`, medications: [{ name: this.newEncounterRx, dose: 'OD' }] }
    }).subscribe({
      next: (res) => {
        this.snackBar.open('Clinical encounter created & vitals logged', 'OK', { duration: 4000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handleSignOffEncounter(encounterId: number): void {
    this.industryService.signOffClinicalEncounter(encounterId, { practitioner_reg_no: 'MCI-2018-9410' }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 4000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handleAddToWaitlist(): void {
    this.industryService.addToHealthcareWaitlist({
      customer_name: 'Aditi Deshmukh',
      customer_phone: '9822334455',
      urgency: 'Urgent',
      preferred_practitioner: 'Dr. Sarah Jenkins',
      notes: 'Request earlier slot on cancellation for cardiac follow-up'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 4000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handlePromoteWaitlist(waitlistId: number): void {
    this.industryService.promoteHealthcareWaitlist(waitlistId).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 4000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handleReserveRoom(): void {
    const start = new Date(Date.now() + 3600000).toISOString();
    const end = new Date(Date.now() + 7200000).toISOString();
    this.industryService.scheduleResourceRoom({
      resource_name: `Consultation Suite ${Math.floor(Math.random() * 5) + 101}`,
      start_time: start,
      end_time: end,
      assigned_practitioner: 'Dr. Sarah Jenkins'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadClinicalCommandCenter();
      },
      error: (err) => {
        this.snackBar.open(err.error?.msg || 'Resource collision detected', 'Dismiss', { duration: 4000 });
      }
    });
  }

  public handleCreateLabOrder(): void {
    const patientId = this.records.length && this.records[0].customer_id ? this.records[0].customer_id : 1;
    this.industryService.createLabOrder({
      customer_id: patientId,
      test_name: 'Complete Metabolic & Lipid Panel',
      category: 'Biochemistry',
      ordering_doctor: 'Dr. Sarah Jenkins'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handleReviewLabOrder(orderId: number): void {
    this.industryService.reviewLabOrder(orderId, {
      doctor_review_notes: 'Biological markers within acceptable clinical parameters.'
    }).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg, 'OK', { duration: 3000 });
        this.loadClinicalCommandCenter();
      }
    });
  }

  public handleIssueAbdmConsent(): void {
    const patientId = this.records.length && this.records[0].customer_id ? this.records[0].customer_id : 1;
    this.industryService.issueAbdmConsent({ patient_id: patientId }).subscribe({
      next: (res) => {
        this.snackBar.open(`ABDM Consent Artifact Issued (Req: ${res.consent.consent_request_id})`, 'OK', { duration: 4000 });
      }
    });
  }

  public loadCustomerUnifiedTimeline(customerId = 1): void {
    this.industryService.getCustomerUnifiedTimeline(customerId).subscribe({
      next: (res) => {
        this.customerTimelineData = res;
        this.activeFeatureModal = 'customer_timeline';
      }
    });
  }

  public handleValidateCustomerImport(): void {
    const sampleRows = [
      { name: 'Dr. Alistair Finch', phone: '9871122334', email: 'alistair@finch.org', tags: 'VIP Client' },
      { name: 'Meera Nambiar', phone: '9845566778', email: 'meera@nambiar.io', tags: 'Corporate' },
      { name: '', phone: '123' } // Intentional invalid test row
    ];
    this.industryService.validateCustomerImport(sampleRows).subscribe({
      next: (res) => {
        this.importValidationSummary = res.summary;
        this.snackBar.open(`Import validation: ${res.summary.valid_count} valid, ${res.summary.error_count} errors`, 'OK', { duration: 4000 });
      }
    });
  }

  public handleRenewSalonMembership(membershipId: string): void {
    this.industryService.renewSalonMembership(membershipId, { renewal_months: 12, fee_amount: 14999 }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 3000 })
    });
  }

  public handleRedeemLoyalty(): void {
    this.industryService.redeemSalonLoyalty({ customer_id: 1, points: 250 }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 3000 })
    });
  }

  public handleReviewFinanceSuitability(): void {
    this.industryService.reviewFinanceSuitability({ customer_id: 1, risk_score: 75 }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 4000 })
    });
  }

  public handleConvertQuoteToPolicy(): void {
    this.industryService.convertQuoteToPolicy({ quote_id: 'Q-PREMIUM-101', carrier: 'Star Health', annual_premium: 26500 }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 4000 })
    });
  }

  public handleVerifyClaimDocs(claimId: string): void {
    this.industryService.verifyClaimDocs(claimId, { claimed_amount: 120000 }).subscribe({
      next: (res) => this.snackBar.open(`TPA Verdict: ${res.underwriting_verdict}`, 'OK', { duration: 4000 })
    });
  }

  public handleCreateRetailOrder(): void {
    this.industryService.createRetailOrder({ customer_name: 'VIP Client' }).subscribe({
      next: (res) => this.snackBar.open(`Sales Order ${res.order_number} created (Total: ₹${res.total_inr.toLocaleString()})`, 'OK', { duration: 4000 })
    });
  }

  public handleConvertEducationLead(): void {
    this.industryService.convertEducationLead({ student_name: 'Aarav Sharma' }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 4000 })
    });
  }

  public handleLegalLimitationDeadlines(): void {
    this.industryService.getLegalLimitationDeadlines().subscribe({
      next: (res) => {
        const count = res.critical_court_deadlines?.length || 0;
        this.snackBar.open(`Court Deadlines: ${count} active matters tracked`, 'OK', { duration: 4000 });
      }
    });
  }

  public handleScheduleSiteVisit(): void {
    this.industryService.scheduleRealEstateSiteVisit({ property_id: 'PROP-SEA-PENTHOUSE' }).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 4000 })
    });
  }

  public handleTimesheetApproval(tsId: string): void {
    this.industryService.approveTimesheet(tsId).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 3000 })
    });
  }

  public handleProjectProfitability(): void {
    this.industryService.getProjectProfitability('PRJ-CLOUD-ENTERPRISE').subscribe({
      next: (res) => {
        this.snackBar.open(`Project Gross Margin: ₹${res.gross_profit_inr.toLocaleString()} (${res.profit_margin_percentage}%)`, 'OK', { duration: 4000 });
      }
    });
  }

  public handleCalcAumFee(): void {
    this.industryService.calculateAdvisoryFees({ aum_inr: 50000000, portfolio_type: 'Growth Equity' }).subscribe({
      next: (res: any) => this.snackBar.open(`Annual AUM Fee: ₹${res.annual_advisory_fee_inr?.toLocaleString()} (${res.effective_fee_percentage}%)`, 'OK', { duration: 4000 })
    });
  }

  public handleCounselorWorkload(): void {
    this.industryService.getCounselorWorkload().subscribe({
      next: (res) => this.snackBar.open(`Counselor Matrix: ${res.total_counselors} counselors managing ${res.active_students_managed} students`, 'OK', { duration: 4000 })
    });
  }

  public handleLegalTimeSignoff(timeId: string): void {
    this.industryService.approveLegalTimeEntry(timeId).subscribe({
      next: (res) => this.snackBar.open(res.msg, 'OK', { duration: 3000 })
    });
  }

  public subscriptionLimitsData: any = null;

  public handleDownloadPrescription(encounterId: number = 1): void {
    this.industryService.downloadEncounterPrescriptionPdf(encounterId).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Prescription_Rx_Encounter_${encounterId}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.snackBar.open('E-Prescription PDF downloaded successfully', 'OK', { duration: 3000 });
      },
      error: () => this.snackBar.open('Could not download prescription PDF', 'Close', { duration: 3000 })
    });
  }

  public handleDownloadInvoice(txnId: number = 1): void {
    this.industryService.downloadTransactionInvoicePdf(txnId).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Tax_Invoice_${txnId}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.snackBar.open('Tax Invoice PDF downloaded successfully', 'OK', { duration: 3000 });
      },
      error: () => this.snackBar.open('Could not download invoice PDF', 'Close', { duration: 3000 })
    });
  }

  public handleGeneratePortalLink(customerId: number = 1): void {
    this.industryService.generateCustomerPortalLink(customerId).subscribe({
      next: (res: any) => {
        this.snackBar.open(`Portal Magic Link: ${res.portal_url} (Code: ${res.auth_code})`, 'Copy', { duration: 6000 });
      },
      error: () => this.snackBar.open('Could not generate portal magic link', 'Close', { duration: 3000 })
    });
  }

  public handleCheckSubscriptionLimits(): void {
    this.industryService.getSubscriptionLimits().subscribe({
      next: (res: any) => {
        this.subscriptionLimitsData = res;
        this.snackBar.open(`Plan: ${res.subscription_plan} | Staff: ${res.staff?.current}/${res.staff?.max} | Branches: ${res.branches?.current}/${res.branches?.max}`, 'OK', { duration: 5000 });
      }
    });
  }

  public closeFeatureModal(): void {
    this.activeFeatureModal = null;
  }
}

