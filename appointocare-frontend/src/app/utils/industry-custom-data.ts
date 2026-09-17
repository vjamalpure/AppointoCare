import { normalizeIndustryKey } from './industry.config';

export interface IndustryCustomFieldDef {
  key: string;
  label: string;
  type: 'text' | 'select' | 'number';
  placeholder?: string;
  options?: string[];
  defaultValue?: string;
  description?: string;
  required?: boolean;
  category?: string;
}

export interface IndustryInfoMessagePreset {
  id: string;
  title: string;
  category: 'prep' | 'documents' | 'directions' | 'confirmation' | 'intake';
  subject: string;
  content: string;
  quickActionLabel: string;
}

export const INDUSTRY_CUSTOM_FIELDS_BY_KEY: Record<string, IndustryCustomFieldDef[]> = {
  healthcare: [
    {
      key: 'triage_priority',
      label: 'Triage Urgency',
      type: 'select',
      options: ['Routine Care', 'Priority Fast-Track', 'Urgent Evaluation', 'Post-Surgical Follow-up'],
      defaultValue: 'Routine Care',
      description: 'Clinical priority level for scheduling and physician review'
    },
    {
      key: 'vitals_summary',
      label: 'Clinical Vitals (BP / Pulse / SpO2)',
      type: 'text',
      placeholder: 'e.g. BP: 120/80 mmHg, HR: 72 bpm, SpO2: 99%, Temp: 98.6°F',
      defaultValue: 'BP: 120/80 mmHg, HR: 72 bpm, SpO2: 99%',
      description: 'Baseline vital signs recorded at check-in or pre-admission'
    },
    {
      key: 'clinical_allergies',
      label: 'Drug & Environmental Allergies',
      type: 'text',
      placeholder: 'e.g. Penicillin, Sulfa, Latex (or None Known)',
      defaultValue: 'None Known',
      description: 'Critical allergy flags for pharmacy and specialist dispensing'
    },
    {
      key: 'fasting_status',
      label: 'Fasting Status for Diagnostic Panels',
      type: 'select',
      options: ['Fasting 8+ Hours (Metabolic Ready)', 'Non-Fasting OK', 'Fasting Required — Not Yet Completed'],
      defaultValue: 'Non-Fasting OK',
      description: 'Required preparation condition for metabolic or lipid panels'
    },
    {
      key: 'chief_complaint',
      label: 'Chief Medical Complaint / Purpose',
      type: 'text',
      placeholder: 'e.g. Annual physical, hypertension management, joint stiffness',
      defaultValue: 'Annual health checkup and preventative screening',
      description: 'Primary reason for the medical consult'
    },
    {
      key: 'insurance_policy_no',
      label: 'Health Insurance Policy / ID',
      type: 'text',
      placeholder: 'e.g. BCBS-9028192-A or Medicare-449102',
      defaultValue: 'BCBS-9028192-A',
      description: 'Primary insurance policy reference for claims submission'
    }
  ],

  finance: [
    {
      key: 'investable_assets',
      label: 'Investable Liquid Asset Tier',
      type: 'select',
      options: ['$100k - $250k Emerging', '$250k - $1M Core Wealth', '$1M - $5M High Net Worth', '$5M+ Ultra HNW / Institutional'],
      defaultValue: '$1M - $5M High Net Worth',
      description: 'Portfolio scale for tier-specific fee schedules and CFA assignment'
    },
    {
      key: 'risk_tolerance',
      label: 'Investment Risk Profile',
      type: 'select',
      options: ['Conservative (Capital Preservation)', 'Moderate Balanced Growth', 'Aggressive Growth & Equity', 'Alternative / Private Debt Focus'],
      defaultValue: 'Moderate Balanced Growth',
      description: 'Suitability benchmark determined via fiduciary questionnaire'
    },
    {
      key: 'advisory_objective',
      label: 'Primary Financial Objective',
      type: 'select',
      options: ['Retirement Drawdown Modeling', 'Tax-Loss Harvesting & Equity Rebalancing', 'Estate & Trust Generational Wealth', 'Corporate Liquidity & Treasury'],
      defaultValue: 'Retirement Drawdown Modeling',
      description: 'Core strategic priority addressed in the consultation'
    },
    {
      key: 'kyc_aml_status',
      label: 'KYC & AML Verification Status',
      type: 'select',
      options: ['KYC Verified & Current', 'Pending Source of Funds Verification', 'Corporate Entity Review Required'],
      defaultValue: 'KYC Verified & Current',
      description: 'Compliance screening status under SEC / FINRA mandates'
    },
    {
      key: 'entity_structure',
      label: 'Account Entity Structure',
      type: 'select',
      options: ['Individual HNW Account', 'Joint Living Trust', 'Family Office / Holding Entity', '501(c)(3) Foundation'],
      defaultValue: 'Individual HNW Account',
      description: 'Tax entity type governing the advisory mandate'
    }
  ],

  retail: [
    {
      key: 'sizing_measurements',
      label: 'Sizing & Tailoring Profile',
      type: 'text',
      placeholder: 'e.g. EU 38 / US 6, Jacket 40R, Inseam 32", Shoe EU 39',
      defaultValue: 'EU 38 / US 6, Shoe EU 39',
      description: 'Precise sizing metrics for styling suite pre-curation'
    },
    {
      key: 'style_aesthetic',
      label: 'Curated Style Aesthetic',
      type: 'select',
      options: ['Haute Couture & Red Carpet', 'Quiet Luxury & Minimalist Tailoring', 'Classic Executive Bespoke', 'Resort & Travel Capsule', 'Contemporary High-Street Luxury'],
      defaultValue: 'Quiet Luxury & Minimalist Tailoring',
      description: 'Aesthetic moodboard preferred by the client'
    },
    {
      key: 'fitting_suite',
      label: 'Reserved VIP Dressing Suite',
      type: 'select',
      options: ['Private Velvet Salon (Level 3)', 'Champagne Penthouse Atelier', 'Bespoke Suiting Suite', 'Bridal & Evening Salon Privé'],
      defaultValue: 'Private Velvet Salon (Level 3)',
      description: 'Assigned private dressing lounge with hospitality service'
    },
    {
      key: 'curation_focus',
      label: 'Occasion & Lookbook Focus',
      type: 'text',
      placeholder: 'e.g. Autumn Milan Fashion Week, Gala Dinner, Capsule Refresh',
      defaultValue: 'Black Tie Gala & Evening Repertoire',
      description: 'Target occasion for the personalized curation'
    },
    {
      key: 'designer_preferences',
      label: 'Preferred Fashion Houses',
      type: 'text',
      placeholder: 'e.g. Brunello Cucinelli, Chanel, Saint Laurent, Loro Piana',
      defaultValue: 'Brunello Cucinelli, Saint Laurent',
      description: 'Specific brand houses requested for the wardrobe pull'
    }
  ],

  insurance: [
    {
      key: 'policy_product_type',
      label: 'Coverage Policy Category',
      type: 'select',
      options: ['Comprehensive Term Life', 'Commercial Property & General Liability', 'Executive Health & Critical Illness', 'Director & Officer (D&O) Liability'],
      defaultValue: 'Comprehensive Term Life',
      description: 'Primary risk policy under consideration or renewal'
    },
    {
      key: 'sum_assured',
      label: 'Sum Insured / Face Amount',
      type: 'select',
      options: ['$250,000', '$500,000', '$1,000,000', '$2,500,000', '$5,000,000 Institutional'],
      defaultValue: '$1,000,000',
      description: 'Total financial coverage underwritten by the carrier'
    },
    {
      key: 'underwriting_tier',
      label: 'Underwriting Risk Classification',
      type: 'select',
      options: ['Preferred Plus (Standard Premium)', 'Standard Underwriting', 'Medical Tele-Interview Required', 'Rated Policy with Exclusion Rider'],
      defaultValue: 'Preferred Plus (Standard Premium)',
      description: 'Risk assessment status determined by actuarial underwriting'
    },
    {
      key: 'claims_history',
      label: 'Prior Claims Record (Past 5 Years)',
      type: 'select',
      options: ['Zero Prior Claims (Clean History)', '1 Minor Settled Claim', 'Prior Loss Under Review'],
      defaultValue: 'Zero Prior Claims (Clean History)',
      description: 'Claims loss history for discount qualification'
    },
    {
      key: 'beneficiary_nomination',
      label: 'Primary Nominee / Beneficiary',
      type: 'text',
      placeholder: 'e.g. Primary: Spouse (100%), Contingent: Family Trust',
      defaultValue: 'Spouse (100% Primary Allocation)',
      description: 'Designated policy beneficiaries and share allocation'
    }
  ],

  education: [
    {
      key: 'target_degree_level',
      label: 'Target Academic Degree Level',
      type: 'select',
      options: ['Undergraduate (BA / BS)', 'Master of Science / Arts (MS / MA)', 'Executive MBA', 'Doctoral PhD Fellowship'],
      defaultValue: 'Undergraduate (BA / BS)',
      description: 'Academic credential level pursued by the student'
    },
    {
      key: 'academic_credentials',
      label: 'Academic Standing (GPA & Test Scores)',
      type: 'text',
      placeholder: 'e.g. GPA: 3.92 / 4.0 unweighted, SAT: 1540, AP Scholar with Distinction',
      defaultValue: 'GPA: 3.92 / 4.0, SAT: 1540, 7 AP Courses',
      description: 'Standardized metrics used for collegiate admissions matching'
    },
    {
      key: 'target_institutions',
      label: 'Aspirational University Shortlist',
      type: 'text',
      placeholder: 'e.g. MIT, Stanford, Oxford, Cambridge, Columbia',
      defaultValue: 'MIT, Stanford, Oxford, Imperial College',
      description: 'Target collegiate institutions for strategy roadmap'
    },
    {
      key: 'target_intake_term',
      label: 'Target Admission Intake Term',
      type: 'select',
      options: ['Fall 2026', 'Spring 2027', 'Fall 2027', 'Rolling Admission'],
      defaultValue: 'Fall 2026',
      description: 'Intended matriculation semester and application cycle'
    },
    {
      key: 'field_of_study',
      label: 'Intended Major / Specialization',
      type: 'text',
      placeholder: 'e.g. Computer Science & AI, Bioengineering, Economics',
      defaultValue: 'Computer Science & Machine Learning',
      description: 'Academic concentration for portfolio alignment'
    }
  ],

  salon: [
    {
      key: 'skin_hair_profile',
      label: 'Skin & Hair Characteristics',
      type: 'text',
      placeholder: 'e.g. Fitzpatrick Type II, Sensitive Dry, Keratin Treated 3B',
      defaultValue: 'Fitzpatrick Type II, Sensitive Dry Skin',
      description: 'Dermatological and trichology attributes for treatment customization'
    },
    {
      key: 'aromatherapy_blend',
      label: 'Organic Aromatherapy Blend',
      type: 'select',
      options: ['French Lavender & Roman Chamomile', 'Revitalizing Eucalyptus & Peppermint', 'Sicilian Bergamot & Neroli', 'Hypoallergenic Fragrance-Free'],
      defaultValue: 'French Lavender & Roman Chamomile',
      description: 'Selected essential oil blend for the wellness treatment'
    },
    {
      key: 'treatment_pressure',
      label: 'Therapeutic Pressure Level',
      type: 'select',
      options: ['Gentle Relaxing Swedish', 'Medium Firm Kinetic', 'Deep Tissue Myofascial', 'Targeted Trigger Point Focus'],
      defaultValue: 'Medium Firm Kinetic',
      description: 'Custom pressure calibration for massage therapies'
    },
    {
      key: 'contraindications',
      label: 'Sensitivities & Contraindications',
      type: 'text',
      placeholder: 'e.g. Active Retinoid use (hold 5 days), Pregnancy-safe only, None',
      defaultValue: 'None (Confirmed Safe)',
      description: 'Safety contraindications to verify prior to application'
    },
    {
      key: 'focus_areas',
      label: 'Targeted Relief & Aesthetic Areas',
      type: 'text',
      placeholder: 'e.g. Cervical spine & trapezius, Facial lymphatic drainage',
      defaultValue: 'Shoulder tension release & facial hydration',
      description: 'Specific focus zones requested by the client'
    }
  ],

  legal: [
    {
      key: 'matter_category',
      label: 'Practice Area & Matter Classification',
      type: 'select',
      options: ['Corporate M&A & Due Diligence', 'Commercial Contract Negotiation', 'IP Protection & Tech Licensing', 'Regulatory Compliance & Anti-Trust', 'Commercial Dispute & Arbitration'],
      defaultValue: 'Corporate M&A & Due Diligence',
      description: 'Legal practice area governing the consultation scope'
    },
    {
      key: 'conflict_check',
      label: 'Conflict of Interest Screening',
      type: 'select',
      options: ['Conflict Check Cleared', 'Screening in Progress', 'Special Partner Waiver Granted'],
      defaultValue: 'Conflict Check Cleared',
      description: 'Mandatory conflict database verification before counsel disclosure'
    },
    {
      key: 'adverse_entities',
      label: 'Screened Adverse & Interested Parties',
      type: 'text',
      placeholder: 'e.g. Nexus Holdings LLC, Apex Global Entities (Screened & Cleared)',
      defaultValue: 'Nexus Holdings LLC (Screened & Cleared)',
      description: 'Counterparties verified against firm conflict registry'
    },
    {
      key: 'privilege_tier',
      label: 'Privilege Classification',
      type: 'select',
      options: ['Attorney-Client Privileged', 'Strict NDA Commercial Secret', 'Standard General Advisory'],
      defaultValue: 'Attorney-Client Privileged',
      description: 'Legal privilege tier applied to all consultation notes'
    },
    {
      key: 'fee_arrangement',
      label: 'Fee Structure & Retainer Model',
      type: 'select',
      options: ['Standard Partner Hourly ($450/hr)', 'Fixed Scope Retainer', 'Capped Monthly General Counsel'],
      defaultValue: 'Fixed Scope Retainer',
      description: 'Billing model established in client engagement letter'
    }
  ],

  realestate: [
    {
      key: 'asset_class',
      label: 'Target Real Estate Asset Class',
      type: 'select',
      options: ['Class A Commercial Office', 'Luxury High-Rise Penthouse', 'Industrial Logistics Hub', 'Prime Retail High-Street'],
      defaultValue: 'Class A Commercial Office',
      description: 'Property category for customized prospectus and valuation'
    },
    {
      key: 'investment_bracket',
      label: 'Target Capital Allocation',
      type: 'select',
      options: ['$500k - $1.5M', '$1.5M - $5M Commercial', '$5M - $25M Institutional', '$25M+ Sovereign / REIT'],
      defaultValue: '$1.5M - $5M Commercial',
      description: 'Buyer or tenant budget parameter for matching'
    },
    {
      key: 'acquisition_timeline',
      label: 'Acquisition / Lease Horizon',
      type: 'select',
      options: ['Immediate (30-Day Closing)', 'Quarterly (60-90 Days)', 'Strategic Long-Term (6-12 Months)'],
      defaultValue: 'Quarterly (60-90 Days)',
      description: 'Target transaction timeframe for broker team'
    },
    {
      key: 'desired_location',
      label: 'Target Submarket / Corridor',
      type: 'text',
      placeholder: 'e.g. Downtown Central Financial District, Waterfront Boulevard',
      defaultValue: 'Downtown Financial Corridor',
      description: 'Geographic submarket preference'
    }
  ],

  custom: [
    {
      key: 'engagement_scope',
      label: 'Scope of Professional Engagement',
      type: 'select',
      options: ['Executive Strategy Alignment', 'Technical Architecture & Cloud Audit', 'Enterprise Process Transformation', 'Bespoke Advisory Retainer'],
      defaultValue: 'Executive Strategy Alignment',
      description: 'Core objective of the enterprise consulting engagement'
    },
    {
      key: 'sla_urgency',
      label: 'Delivery SLA & Priority',
      type: 'select',
      options: ['Mission-Critical (24/7 SLA)', 'High Priority (Same-Day Response)', 'Standard Professional SLA'],
      defaultValue: 'High Priority (Same-Day Response)',
      description: 'Response and deliverable timeframe commitment'
    },
    {
      key: 'stakeholder_team',
      label: 'Client Stakeholder Attendees',
      type: 'text',
      placeholder: 'e.g. VP Engineering, CTO, 4 Technical Architects',
      defaultValue: 'VP Engineering & Architecture Leads',
      description: 'Participants expected for the strategic engagement'
    }
  ]
};

export const INDUSTRY_INFO_MESSAGES_BY_KEY: Record<string, IndustryInfoMessagePreset[]> = {
  healthcare: [
    {
      id: 'hc_prep',
      title: 'Fasting & Diagnostic Preparation Guide',
      category: 'prep',
      subject: 'Clinical Fasting & Lab Prep Protocol',
      content: 'Hello {customer_name}, for your upcoming clinical appointment at {organization_name}, please follow these preparation guidelines:\n• If fasting bloodwork is scheduled, drink only water for 8 hours prior.\n• Take your regular morning medications unless specifically instructed otherwise.\n• Please arrive 10 minutes early with your photo ID and insurance card.',
      quickActionLabel: 'Send Fasting & Prep Guide'
    },
    {
      id: 'hc_docs',
      title: 'Required Medical Records & ID Checklist',
      category: 'documents',
      subject: 'Required Documents for Clinical Check-In',
      content: 'Hello {customer_name}, to expedite your check-in at {organization_name} ({branch_name}), please bring:\n1. Valid Government Photo ID (Passport or Driver License)\n2. Primary Health Insurance Card & Group Number\n3. Recent lab reports or clinical summaries\n4. Complete list of current prescriptions.',
      quickActionLabel: 'Send Records Checklist'
    },
    {
      id: 'hc_directions',
      title: 'Clinic Location & Parking Instructions',
      category: 'directions',
      subject: 'Clinic Address & Dedicated Patient Parking',
      content: 'Hello {customer_name}, your consultation is at {organization_name} — {branch_name} ({branch_address}).\n• Dedicated patient parking is available in Lot B with complimentary validation.\n• Please proceed to Reception on Floor 2 to complete check-in.',
      quickActionLabel: 'Send Clinic Directions'
    },
    {
      id: 'hc_confirm',
      title: 'Appointment Confirmation & Payment Link',
      category: 'confirmation',
      subject: 'Confirmed Clinical Appointment with {staff_name}',
      content: 'Hello {customer_name}, your appointment for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nSecure Razorpay Payment Link: https://appointocare.com/pay/{appointment_id}\n\nReply to this message if you have any questions before your visit.',
      quickActionLabel: 'Send Confirmation & Payment'
    }
  ],

  finance: [
    {
      id: 'fin_prep',
      title: 'Pre-Session Portfolio Discovery Packet',
      category: 'prep',
      subject: 'Wealth Advisory Pre-Consultation Discovery',
      content: 'Dear {customer_name}, in preparation for your confidential advisory session with Senior Advisor {staff_name} at {organization_name}, we invite you to review our discovery checklist. Having your recent brokerage summaries and tax records accessible will help us model your financial objectives effectively.',
      quickActionLabel: 'Send Discovery Packet'
    },
    {
      id: 'fin_docs',
      title: 'KYC & Fiduciary Compliance Checklist',
      category: 'documents',
      subject: 'Required Fiduciary Onboarding Documents',
      content: 'Dear {customer_name}, under fiduciary standards, please submit or bring the following for your consultation at {organization_name}:\n1. Government Photo ID and proof of primary residence\n2. Recent account statement or asset holdings summary\n3. Existing estate plan or trust deed (if applicable).',
      quickActionLabel: 'Send KYC Checklist'
    },
    {
      id: 'fin_directions',
      title: 'Executive Advisory Suite & Valet Parking',
      category: 'directions',
      subject: 'Advisory Office Location & Private Valet',
      content: 'Dear {customer_name}, your private consultation is scheduled at our {branch_name} offices located at {branch_address}.\n• Complimentary valet parking is available at the building main portico.\n• Please check in with the Executive Concierge on Floor 14.',
      quickActionLabel: 'Send Office Location'
    },
    {
      id: 'fin_confirm',
      title: 'Advisory Session Confirmation & Fee Schedule',
      category: 'confirmation',
      subject: 'Confirmed Advisory Consultation with {staff_name}',
      content: 'Dear {customer_name}, your financial advisory consultation for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nRetainer / Fee Invoice: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to partnering on your long-term wealth roadmap.',
      quickActionLabel: 'Send Confirmation & Invoice'
    }
  ],

  retail: [
    {
      id: 'ret_prep',
      title: 'VIP Styling Pre-Curation Lookbook',
      category: 'prep',
      subject: 'Personal Styling Session & Wardrobe Moodboard',
      content: 'Hello {customer_name}! Your dedicated Personal Stylist {staff_name} is currently pre-selecting garments for your session at {organization_name}. If there are specific silhouettes, color palettes, or designers you would like included, please message us your preferences here.',
      quickActionLabel: 'Send Styling Moodboard'
    },
    {
      id: 'ret_docs',
      title: 'Bespoke Measurement & Tailoring Guide',
      category: 'documents',
      subject: 'Bespoke Measurements & Tailoring Preferences',
      content: 'Hello {customer_name}, during your appointment at {organization_name} ({branch_name}), our Master Tailor will record precise measurements. If you wish to bring existing bespoke suits or dresses for fine adjustment, our tailoring team will gladly review them.',
      quickActionLabel: 'Send Measurement Guide'
    },
    {
      id: 'ret_directions',
      title: 'VIP Private Atelier Entrance & Champagne Suite',
      category: 'directions',
      subject: 'VIP Salon Privé Entrance & Reserved Suite',
      content: 'Hello {customer_name}, your private styling salon is reserved at {branch_name} ({branch_address}).\n• Please use the VIP private entrance on the West Courtyard.\n• Your complimentary champagne refreshment bar is reserved upon arrival.',
      quickActionLabel: 'Send VIP Lounge Access'
    },
    {
      id: 'ret_confirm',
      title: 'VIP Styling Appointment Confirmation',
      category: 'confirmation',
      subject: 'Confirmed Personal Styling Appointment with {staff_name}',
      content: 'Hello {customer_name}, your VIP styling session for {service_name} with {staff_name} is confirmed for {appointment_date} at {organization_name} ({branch_name}).\n\nBooking Deposit Link: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to welcoming you to the salon.',
      quickActionLabel: 'Send Confirmation & Deposit'
    }
  ],

  insurance: [
    {
      id: 'ins_prep',
      title: 'Policy Underwriting Questionnaire Guide',
      category: 'prep',
      subject: 'Insurance Policy Underwriting Prep Guide',
      content: 'Hello {customer_name}, for your policy consultation with {staff_name} at {organization_name}, please review your current coverage summary. Having your family medical history and primary assets outlined will expedite your underwriting quote.',
      quickActionLabel: 'Send Underwriting Guide'
    },
    {
      id: 'ins_docs',
      title: 'Required Verification & Nominee Documents',
      category: 'documents',
      subject: 'Required Documents for Policy Binding',
      content: 'Hello {customer_name}, to bind your insurance coverage at {organization_name} ({branch_name}), please have available:\n1. Proof of identity and date of birth\n2. Proof of income or audited financials (for high-sum policies)\n3. Primary and contingent beneficiary details and SSN/ID.',
      quickActionLabel: 'Send Policy Checklist'
    },
    {
      id: 'ins_directions',
      title: 'Agency Branch Location & Consultation Room',
      category: 'directions',
      subject: 'Insurance Agency Office Location & Directions',
      content: 'Hello {customer_name}, your policy review is scheduled at {organization_name} — {branch_name} ({branch_address}).\n• Free visitor parking is located in the front agency plaza.\n• Please ask for {staff_name} at the main reception desk.',
      quickActionLabel: 'Send Agency Directions'
    },
    {
      id: 'ins_confirm',
      title: 'Coverage Review Confirmation & Premium Link',
      category: 'confirmation',
      subject: 'Confirmed Insurance Review with {staff_name}',
      content: 'Hello {customer_name}, your appointment for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nInitial Premium Payment Link: https://appointocare.com/pay/{appointment_id}\n\nFeel free to message us here with any policy questions.',
      quickActionLabel: 'Send Confirmation & Premium'
    }
  ],

  education: [
    {
      id: 'edu_prep',
      title: 'Academic Profile & Portfolio Preparation',
      category: 'prep',
      subject: 'Admissions Strategy Pre-Session Guide',
      content: 'Hello {customer_name}, in preparation for your academic counseling session with Dr. {staff_name} at {organization_name}, please have your unweighted GPA, standardized test score reports (SAT/ACT/IELTS), and current extracurricular activity list ready for review.',
      quickActionLabel: 'Send Portfolio Prep Guide'
    },
    {
      id: 'edu_docs',
      title: 'Transcripts & Testing Score Submission',
      category: 'documents',
      subject: 'Required Academic Transcripts for Strategy Review',
      content: 'Hello {customer_name}, to tailor your university roadmap at {organization_name} ({branch_name}), please bring or email:\n1. High school / collegiate official transcripts (grades 9-12)\n2. Standardized testing score reports\n3. Draft personal statement or college wishlist.',
      quickActionLabel: 'Send Transcript Checklist'
    },
    {
      id: 'edu_directions',
      title: 'Academic Hub Location & Video Conference Link',
      category: 'directions',
      subject: 'Counseling Hub Address & Virtual Conference Access',
      content: 'Hello {customer_name}, your session with Dr. {staff_name} is at {organization_name} — {branch_name} ({branch_address}).\n• If attending virtually, your dedicated secure video room is: https://appointocare.com/meet/{appointment_id}\n• For in-person meetings, guest parking is available in the academic campus lot.',
      quickActionLabel: 'Send Hub Directions'
    },
    {
      id: 'edu_confirm',
      title: 'University Counseling Session Confirmation',
      category: 'confirmation',
      subject: 'Confirmed Academic Counseling with {staff_name}',
      content: 'Hello {customer_name}, your academic counseling session for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nTuition / Advisory Fee Link: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to helping you achieve your admissions goals.',
      quickActionLabel: 'Send Confirmation & Fee Link'
    }
  ],

  salon: [
    {
      id: 'sal_prep',
      title: 'Spa Treatment Pre-Care & Skin Guidelines',
      category: 'prep',
      subject: 'Treatment Preparation & Skin Care Guidelines',
      content: 'Hello {customer_name}, to ensure the most relaxing experience at {organization_name} ({branch_name}), please arrive 10 minutes before your ritual. We suggest wearing comfortable attire. Please refrain from active chemical peels or retinoids 48 hours prior to facial treatments.',
      quickActionLabel: 'Send Spa Pre-Care Guide'
    },
    {
      id: 'sal_docs',
      title: 'Aromatherapy & Sensory Customization Menu',
      category: 'documents',
      subject: 'Organic Essential Oils & Pressure Selection',
      content: 'Hello {customer_name}, your appointment with {staff_name} includes customized aromatherapy. Our organic blends include French Lavender & Chamomile (Calming), Eucalyptus & Mint (Invigorating), or Hypoallergenic Fragrance-Free. Let your aesthetician know your preference upon arrival.',
      quickActionLabel: 'Send Aromatherapy Menu'
    },
    {
      id: 'sal_directions',
      title: 'Spa Lounge Location & Robe Fitting',
      category: 'directions',
      subject: 'Spa Location & Relaxation Lounge Amenities',
      content: 'Hello {customer_name}, your ritual takes place at {organization_name} — {branch_name} ({branch_address}).\n• Complimentary herbal infusions and robe fittings are available in the Quiet Lounge.\n• Please check in at our Wellness Reception desk.',
      quickActionLabel: 'Send Spa Location'
    },
    {
      id: 'sal_confirm',
      title: 'Spa Ritual Confirmation & Reservation Deposit',
      category: 'confirmation',
      subject: 'Confirmed Wellness Ritual with {staff_name}',
      content: 'Hello {customer_name}, your wellness appointment for {service_name} with {staff_name} is confirmed for {appointment_date} at {organization_name} ({branch_name}).\n\nOnline Payment Link: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to pampering you.',
      quickActionLabel: 'Send Confirmation & Pay Link'
    }
  ],

  legal: [
    {
      id: 'leg_prep',
      title: 'Legal Briefing & Confidentiality Protocol',
      category: 'prep',
      subject: 'Confidential Consultation Protocol & Retainer Guide',
      content: 'Dear {customer_name}, your consultation with Senior Counsel {staff_name} at {organization_name} is protected under Attorney-Client Privilege. To optimize our session, please prepare a chronological summary of facts and key commercial counterparties.',
      quickActionLabel: 'Send Privilege Protocol'
    },
    {
      id: 'leg_docs',
      title: 'Conflict Clearance & Document Upload Room',
      category: 'documents',
      subject: 'Conflict Screening & Secure Evidence Room',
      content: 'Dear {customer_name}, before our strategic counsel session at {organization_name} ({branch_name}), please confirm:\n1. All adverse entities or interested parties have been disclosed for conflict screening\n2. Upload disputed contracts or draft transaction agreements to our secure client portal.',
      quickActionLabel: 'Send Conflict Checklist'
    },
    {
      id: 'leg_directions',
      title: 'Chambers Location & Conference Suite',
      category: 'directions',
      subject: 'Law Chambers Location & Executive Conference Room',
      content: 'Dear {customer_name}, your confidential meeting is scheduled at {organization_name} — {branch_name} ({branch_address}).\n• Please present your photo ID at the building security desk on Floor 1.\n• You will be escorted to Executive Conference Room A.',
      quickActionLabel: 'Send Chambers Directions'
    },
    {
      id: 'leg_confirm',
      title: 'Legal Consultation Confirmation & Retainer Invoice',
      category: 'confirmation',
      subject: 'Confirmed Legal Consultation with {staff_name}',
      content: 'Dear {customer_name}, your legal consultation for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nTrust Account Retainer Invoice: https://appointocare.com/pay/{appointment_id}\n\nAll disclosures will be handled with strict confidentiality.',
      quickActionLabel: 'Send Confirmation & Retainer'
    }
  ],

  realestate: [
    {
      id: 're_prep',
      title: 'Private Property Portfolio & Valuation Dossier',
      category: 'prep',
      subject: 'Property Valuation & Acquisition Dossier',
      content: 'Hello {customer_name}, your Senior Broker {staff_name} at {organization_name} has curated an exclusive property prospectus tailored to your investment bracket. We will review comparative cap rates and zoning permits during our session.',
      quickActionLabel: 'Send Property Dossier'
    },
    {
      id: 're_docs',
      title: 'Proof of Funds & Pre-Approval Checklist',
      category: 'documents',
      subject: 'Required Buyer Due Diligence & Pre-Approval',
      content: 'Hello {customer_name}, for private site inspections with {organization_name} ({branch_name}), please have available:\n1. Lender pre-approval letter or proof of liquid funds\n2. Preferred LLC / acquisition entity name\n3. Target 1031 exchange timeline (if applicable).',
      quickActionLabel: 'Send Buyer Checklist'
    },
    {
      id: 're_directions',
      title: 'Property Tour Meeting Point & Parking',
      category: 'directions',
      subject: 'Property Viewing Meeting Point & Parking Logistics',
      content: 'Hello {customer_name}, our site tour meeting point is at {organization_name} — {branch_name} ({branch_address}).\n• Private parking is available in the broker bay.\n• We will proceed together via broker transit to the target properties.',
      quickActionLabel: 'Send Tour Meeting Point'
    },
    {
      id: 're_confirm',
      title: 'Property Advisory Appointment Confirmation',
      category: 'confirmation',
      subject: 'Confirmed Real Estate Tour with {staff_name}',
      content: 'Hello {customer_name}, your property tour for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nRetainer / Advisory Deposit Link: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to presenting your tailored portfolio.',
      quickActionLabel: 'Send Confirmation & Link'
    }
  ],

  custom: [
    {
      id: 'cust_prep',
      title: 'Enterprise Statement of Work (SOW) Briefing',
      category: 'prep',
      subject: 'Enterprise Consultation Scope & SOW Review',
      content: 'Dear {customer_name}, ahead of our executive engagement with {staff_name} at {organization_name}, please review our preliminary statement of work. Having your technical architecture diagrams and operational KPIs accessible will enable an actionable roadmap.',
      quickActionLabel: 'Send SOW Briefing'
    },
    {
      id: 'cust_docs',
      title: 'Required Corporate NDA & Architecture Specs',
      category: 'documents',
      subject: 'Mutual NDA & Technical Architecture Submission',
      content: 'Dear {customer_name}, to optimize our enterprise consultation at {organization_name} ({branch_name}), please share:\n1. Executed mutual non-disclosure agreement (MNDA)\n2. Cloud infrastructure topology or organizational workflow charts\n3. Key executive attendee roster.',
      quickActionLabel: 'Send Enterprise Checklist'
    },
    {
      id: 'cust_directions',
      title: 'Executive Briefing Center Location',
      category: 'directions',
      subject: 'Executive Briefing Center Location & Access Code',
      content: 'Dear {customer_name}, your enterprise strategic session is hosted at {organization_name} — {branch_name} ({branch_address}).\n• Visitor security badges can be collected with photo ID at the West Lobby.\n• Executive Suite 500 is reserved for your team.',
      quickActionLabel: 'Send Center Directions'
    },
    {
      id: 'cust_confirm',
      title: 'Enterprise Engagement Confirmation & Retainer',
      category: 'confirmation',
      subject: 'Confirmed Enterprise Consultation with {staff_name}',
      content: 'Dear {customer_name}, your enterprise consultation for {service_name} with {staff_name} is confirmed for {appointment_date} at {branch_name}.\n\nProfessional Retainer Invoice: https://appointocare.com/pay/{appointment_id}\n\nWe look forward to partnering with your leadership team.',
      quickActionLabel: 'Send Confirmation & Retainer'
    }
  ]
};

/**
 * Returns custom fields configured for a specific industry.
 */
export function getIndustryCustomFields(templateOrSector?: string | null): IndustryCustomFieldDef[] {
  const key = normalizeIndustryKey(templateOrSector);
  return (INDUSTRY_CUSTOM_FIELDS_BY_KEY[key] || INDUSTRY_CUSTOM_FIELDS_BY_KEY['healthcare']) as IndustryCustomFieldDef[];
}

/**
 * Returns pre-built WhatsApp/portal necessary info messages for an industry.
 */
export function getIndustryInfoMessages(templateOrSector?: string | null): IndustryInfoMessagePreset[] {
  const key = normalizeIndustryKey(templateOrSector);
  return (INDUSTRY_INFO_MESSAGES_BY_KEY[key] || INDUSTRY_INFO_MESSAGES_BY_KEY['healthcare']) as IndustryInfoMessagePreset[];
}

/**
 * Builds default custom fields map for a new appointment in this industry.
 */
export function getDefaultIndustryCustomFields(templateOrSector?: string | null): Record<string, string> {
  const fields = getIndustryCustomFields(templateOrSector);
  const result: Record<string, string> = {};
  for (const f of fields) {
    if (f.defaultValue) {
      result[f.key] = f.defaultValue;
    }
  }
  return result;
}

/**
 * Formats a short scannable text summary of custom fields for badges/cards.
 */
export function formatIndustryCustomFieldsSummary(customFields?: Record<string, any>, templateOrSector?: string | null): string {
  if (!customFields || Object.keys(customFields).length === 0) {
    return 'Standard Intake';
  }
  const key = normalizeIndustryKey(templateOrSector);
  if (key === 'healthcare') {
    return `${customFields['triage_priority'] || 'Routine'} • ${customFields['fasting_status'] || 'Non-Fasting'}`;
  }
  if (key === 'finance') {
    return `${customFields['investable_assets'] || 'Core Wealth'} • ${customFields['risk_tolerance'] || 'Balanced'}`;
  }
  if (key === 'retail') {
    return `${customFields['style_aesthetic'] || 'Couture'} • Suite: ${customFields['fitting_suite'] ? String(customFields['fitting_suite']).split('(')[0].trim() : 'VIP'}`;
  }
  if (key === 'insurance') {
    return `${customFields['policy_product_type'] || 'Term Life'} • Sum: ${customFields['sum_assured'] || '$1M'}`;
  }
  if (key === 'education') {
    return `${customFields['target_degree_level'] || 'Undergrad'} • ${customFields['target_intake_term'] || 'Fall 2026'}`;
  }
  if (key === 'salon') {
    return `${customFields['treatment_pressure'] || 'Medium'} • ${customFields['aromatherapy_blend'] ? String(customFields['aromatherapy_blend']).split('&')[0].trim() : 'Lavender'}`;
  }
  if (key === 'legal') {
    return `${customFields['matter_category'] || 'Corporate M&A'} • ${customFields['conflict_check'] || 'Cleared'}`;
  }
  if (key === 'realestate') {
    return `${customFields['asset_class'] || 'Commercial'} • Budget: ${customFields['investment_bracket'] || '$1.5M - $5M'}`;
  }
  return `${customFields['engagement_scope'] || 'Strategic'} • SLA: ${customFields['sla_urgency'] || 'High'}`;
}
