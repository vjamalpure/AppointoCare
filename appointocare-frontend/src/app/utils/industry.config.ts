import {
  getIndustryCustomFields,
  getIndustryInfoMessages,
  getDefaultIndustryCustomFields,
  formatIndustryCustomFieldsSummary,
  IndustryCustomFieldDef,
  IndustryInfoMessagePreset
} from './industry-custom-data';

export interface IndustryServicePreset {
  name: string;
  category: string;
  duration_minutes: number;
  price: number;
  description: string;
}

export interface IndustryConfig {
  id: string;
  name: string;
  sector: string;
  description?: string;
  defaultServices?: IndustryServicePreset[];
  badgeColor: {
    bg: string;
    text: string;
    border: string;
    accent: string;
  };
  organizationLabel: string;
  organizationPluralLabel: string;
  customerLabel: string;
  customerPluralLabel: string;
  customerIdentifierLabel: string; // e.g. "Patient MRN", "Client Portfolio ID", "VIP Account #"
  customerNotesLabel: string; // e.g. "Medical Allergies & History", "Risk Tolerance & Goals", "Measurements & Style Notes"
  staffLabel: string;
  staffPluralLabel: string;
  appointmentLabel: string;
  appointmentPluralLabel: string;
  branchLabel: string;
  branchPluralLabel: string;
  serviceLabel: string;
  servicePluralLabel: string;
  sampleBookingNotes: string;
  defaultWhatsAppTemplate: string;
  servicePresets: IndustryServicePreset[];
  sampleCustomerTags: string[];
}

export const INDUSTRY_CONFIGS: Record<string, IndustryConfig> = {
  healthcare: {
    id: 'healthcare',
    name: 'Hospital & Medical Clinic',
    sector: 'Healthcare',
    badgeColor: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      text: 'text-emerald-700',
      border: 'border-emerald-300',
      accent: 'emerald'
    },
    organizationLabel: 'Clinic / Medical Center',
    organizationPluralLabel: 'Clinics & Centers',
    customerLabel: 'Patient',
    customerPluralLabel: 'Patients',
    customerIdentifierLabel: 'Medical Record # (MRN)',
    customerNotesLabel: 'Clinical Allergies & Medical History',
    staffLabel: 'Doctor / Specialist',
    staffPluralLabel: 'Medical Staff & Doctors',
    appointmentLabel: 'Appointment',
    appointmentPluralLabel: 'Appointments',
    branchLabel: 'Clinic Branch',
    branchPluralLabel: 'Clinic Branches',
    serviceLabel: 'Medical Treatment / Consult',
    servicePluralLabel: 'Clinical Services',
    sampleBookingNotes: 'Patient reports mild throat soreness and requests annual diagnostic fasting blood panel.',
    defaultWhatsAppTemplate: 'Hello {customer_name}, your clinical appointment for {service_name} at {organization_name} ({branch_name}) is confirmed for {appointment_date} with {staff_name}. Note: {notes}. Please arrive 10 minutes early.',
    sampleCustomerTags: ['High Priority', 'Chronic Care', 'Fasting Required', 'Insurance Verified', 'Pediatric'],
    servicePresets: [
      {
        name: 'General Physician Consultation',
        category: 'Consultation',
        duration_minutes: 30,
        price: 60,
        description: 'Comprehensive physical examination, vital signs check, diagnostic review, and clinical prescription.'
      },
      {
        name: 'Specialist Evaluation (Cardiology/ENT)',
        category: 'Specialist',
        duration_minutes: 45,
        price: 120,
        description: 'In-depth specialist diagnostic assessment, symptom analysis, and targeted treatment regimen.'
      },
      {
        name: 'Comprehensive Health & Blood Panel',
        category: 'Diagnostics',
        duration_minutes: 60,
        price: 150,
        description: 'Full metabolic blood screening, complete lipid panel, CBC, renal and liver function evaluation.'
      },
      {
        name: 'Dental Cleaning & Oral Exam',
        category: 'Dental',
        duration_minutes: 45,
        price: 85,
        description: 'Ultrasonic plaque removal, subgingival scaling, fluoride polish, and digital bitewing X-rays.'
      },
      {
        name: 'Physiotherapy Rehabilitation',
        category: 'Therapy',
        duration_minutes: 60,
        price: 90,
        description: 'Musculoskeletal kinetic assessment, manual joint mobilization, and guided recovery exercise protocols.'
      }
    ]
  },

  finance: {
    id: 'finance',
    name: 'Wealth & Financial Advisory',
    sector: 'Finance',
    badgeColor: {
      bg: 'bg-indigo-50 text-indigo-700 border-indigo-200',
      text: 'text-indigo-700',
      border: 'border-indigo-300',
      accent: 'indigo'
    },
    organizationLabel: 'Advisory Firm / Practice',
    organizationPluralLabel: 'Advisory Firms',
    customerLabel: 'Client / Investor',
    customerPluralLabel: 'Clients & Investors',
    customerIdentifierLabel: 'Portfolio / Account ID',
    customerNotesLabel: 'Risk Tolerance & Investment Objectives',
    staffLabel: 'Wealth Advisor / CFA',
    staffPluralLabel: 'Financial Advisors & Managers',
    appointmentLabel: 'Advisory Consultation',
    appointmentPluralLabel: 'Advisory Consultations',
    branchLabel: 'Advisory Office',
    branchPluralLabel: 'Advisory Offices',
    serviceLabel: 'Advisory Package / Plan',
    servicePluralLabel: 'Financial Services',
    sampleBookingNotes: 'Client seeking Q4 tax-loss harvesting advice, dividend reinvestment review, and retirement drawdown strategy.',
    defaultWhatsAppTemplate: 'Dear {customer_name}, your confidential financial consultation for {service_name} with Senior Advisor {staff_name} is confirmed for {appointment_date} at {organization_name} ({branch_name}).',
    sampleCustomerTags: ['High Net Worth', 'Accredited Investor', 'Trust & Estate', 'Retirement Planning', 'Private Equity'],
    servicePresets: [
      {
        name: 'Investment & Wealth Portfolio Review',
        category: 'Wealth',
        duration_minutes: 60,
        price: 180,
        description: 'Asset allocation rebalancing, macroeconomic risk assessment, alpha yield tuning, and retirement modeling.'
      },
      {
        name: 'Personal Loan & Mortgage Consultation',
        category: 'Lending',
        duration_minutes: 45,
        price: 75,
        description: 'Fixed vs variable interest rates structuring, debt consolidation analysis, and amortisation roadmap.'
      },
      {
        name: 'Tax Filing & Assessment Planning',
        category: 'Tax Strategy',
        duration_minutes: 45,
        price: 110,
        description: 'Capital gains optimization, cross-border tax shelter compliance, and corporate tax liability reduction.'
      },
      {
        name: 'Business Audit & Credit Structuring',
        category: 'Corporate',
        duration_minutes: 90,
        price: 250,
        description: 'Corporate balance sheet stress-testing, commercial debt refinancing, and venture equity advisory.'
      }
    ]
  },

  retail: {
    id: 'retail',
    name: 'Luxury Retail & Personal Styling',
    sector: 'Retail',
    badgeColor: {
      bg: 'bg-amber-50 text-amber-700 border-amber-200',
      text: 'text-amber-700',
      border: 'border-amber-300',
      accent: 'amber'
    },
    organizationLabel: 'Fashion House / Lounge',
    organizationPluralLabel: 'Fashion Lounges & Boutiques',
    customerLabel: 'VIP Client',
    customerPluralLabel: 'VIP Clients',
    customerIdentifierLabel: 'VIP Client Tier / ID',
    customerNotesLabel: 'Wardrobe Sizes & Styling Preferences',
    staffLabel: 'Personal Stylist / Curator',
    staffPluralLabel: 'Stylists & Fashion Curators',
    appointmentLabel: 'Styling Session',
    appointmentPluralLabel: 'Styling Sessions',
    branchLabel: 'Boutique / Showroom',
    branchPluralLabel: 'Boutiques & Showrooms',
    serviceLabel: 'Styling Experience',
    servicePluralLabel: 'Styling & Fitting Catalog',
    sampleBookingNotes: 'Client attending black-tie gala. Prefers silk organza and jewel tones; needs accessory pairing.',
    defaultWhatsAppTemplate: 'Welcome {customer_name}! Your private styling session for {service_name} is reserved on {appointment_date} at {organization_name} ({branch_name}) with Stylist {staff_name}. Refreshments provided.',
    sampleCustomerTags: ['Haute Couture', 'Private Suite', 'Bridal', 'Frequent Shopper', 'Made-to-Measure'],
    servicePresets: [
      {
        name: 'VIP Private Styling & Fitting',
        category: 'Styling',
        duration_minutes: 60,
        price: 100,
        description: 'One-on-one wardrobe curation, silhouette analysis, and private dressing lounge fitting with refreshments.'
      },
      {
        name: 'Bridal & Bespoke Wardrobe Session',
        category: 'Bespoke',
        duration_minutes: 90,
        price: 220,
        description: 'Custom bridal gown consultation, fabric swatches selection, veil pairing, and artisan tailor measurements.'
      },
      {
        name: 'High-Jewelry Private Viewing Suite',
        category: 'Fine Jewelry',
        duration_minutes: 45,
        price: 150,
        description: 'Champagne viewing of rare gemstone parures, diamond grading review, and vault security escort.'
      },
      {
        name: 'Seasonal Wardrobe Refresh & Fitting',
        category: 'Curation',
        duration_minutes: 60,
        price: 120,
        description: 'Complete capsule wardrobe build, international trend alignment, and tailored alterations review.'
      }
    ]
  },

  insurance: {
    id: 'insurance',
    name: 'Life & General Insurance Agency',
    sector: 'Insurance',
    badgeColor: {
      bg: 'bg-cyan-50 text-cyan-700 border-cyan-200',
      text: 'text-cyan-700',
      border: 'border-cyan-300',
      accent: 'cyan'
    },
    organizationLabel: 'Insurance Agency',
    organizationPluralLabel: 'Insurance Agencies',
    customerLabel: 'Policyholder / Client',
    customerPluralLabel: 'Policyholders',
    customerIdentifierLabel: 'Policy # / Claim Reference',
    customerNotesLabel: 'Coverage Limits & Risk Factors',
    staffLabel: 'Insurance Agent / Broker',
    staffPluralLabel: 'Agents & Underwriters',
    appointmentLabel: 'Policy Consultation',
    appointmentPluralLabel: 'Policy Consultations',
    branchLabel: 'Agency Branch Office',
    branchPluralLabel: 'Agency Offices',
    serviceLabel: 'Insurance Product Review',
    servicePluralLabel: 'Insurance & Coverage Products',
    sampleBookingNotes: 'Client purchasing commercial liability umbrella policy; needs fleet vehicle coverage analysis.',
    defaultWhatsAppTemplate: 'Hello {customer_name}, your insurance policy review for {service_name} is scheduled for {appointment_date} at {organization_name} ({branch_name}). Licensed Agent: {staff_name}.',
    sampleCustomerTags: ['Term Life', 'Commercial Fleet', 'Pending Claim', 'Annual Review', 'High Coverage'],
    servicePresets: [
      {
        name: 'Term & Life Insurance Policy Advisory',
        category: 'Life & Health',
        duration_minutes: 45,
        price: 65,
        description: 'Actuarial mortality analysis, whole life vs term comparison, cash value rider review, and beneficiary designation.'
      },
      {
        name: 'Health Insurance Claims Review',
        category: 'Claims',
        duration_minutes: 30,
        price: 50,
        description: 'Deductible verification, pre-authorization appeal assistance, co-insurance calculation, and claim settlement filing.'
      },
      {
        name: 'Commercial & Motor Risk Assessment',
        category: 'Commercial',
        duration_minutes: 60,
        price: 120,
        description: 'Property liability underwriting, fleet hazard inspection, business interruption rider, and workman compensation review.'
      }
    ]
  },

  education: {
    id: 'education',
    name: 'Academy & University Counseling',
    sector: 'Education',
    badgeColor: {
      bg: 'bg-blue-50 text-blue-700 border-blue-200',
      text: 'text-blue-700',
      border: 'border-blue-300',
      accent: 'blue'
    },
    organizationLabel: 'Academy / Counseling Hub',
    organizationPluralLabel: 'Academies & Centers',
    customerLabel: 'Student / Applicant',
    customerPluralLabel: 'Students & Applicants',
    customerIdentifierLabel: 'Student Enrollment ID',
    customerNotesLabel: 'Academic GPA & Target Universities',
    staffLabel: 'Academic Counselor / Advisor',
    staffPluralLabel: 'Counselors & Faculty',
    appointmentLabel: 'Counseling Session',
    appointmentPluralLabel: 'Counseling Sessions',
    branchLabel: 'Campus / Center',
    branchPluralLabel: 'Campuses & Centers',
    serviceLabel: 'Counseling / Tutoring Program',
    servicePluralLabel: 'Academic Programs',
    sampleBookingNotes: 'High-school senior applying to Ivy League engineering. Essay review and standardized test score roadmap.',
    defaultWhatsAppTemplate: 'Hi {customer_name}, your academic counseling session for {service_name} is scheduled on {appointment_date} with Counselor {staff_name} at {organization_name} ({branch_name}).',
    sampleCustomerTags: ['Ivy League Prep', 'Undergraduate', 'Postgraduate', 'SAT/ACT Coaching', 'Scholarship Candidate'],
    servicePresets: [
      {
        name: 'Academic Course Guidance & Planning',
        category: 'Counseling',
        duration_minutes: 45,
        price: 60,
        description: 'Curriculum credit mapping, AP/IB course selection, GPA optimization strategy, and semester scheduling.'
      },
      {
        name: 'University Admission Interview Prep',
        category: 'Admissions',
        duration_minutes: 60,
        price: 120,
        description: 'Mock collegiate admissions interview, body language coaching, personal statement critique, and Dean response drills.'
      },
      {
        name: 'Career Counseling & Aptitude Analysis',
        category: 'Career Guidance',
        duration_minutes: 60,
        price: 95,
        description: 'Psychometric career aptitude testing, industry salary trajectories analysis, and university major matching.'
      },
      {
        name: '1-on-1 Academic Tutoring Session',
        category: 'Tutoring',
        duration_minutes: 45,
        price: 50,
        description: 'Advanced STEM problem-solving, thesis argumentation breakdown, and targeted exam prep.'
      }
    ]
  },

  salon: {
    id: 'salon',
    name: 'Premium Salon & Aesthetics Spa',
    sector: 'Salon & Wellness',
    badgeColor: {
      bg: 'bg-rose-50 text-rose-700 border-rose-200',
      text: 'text-rose-700',
      border: 'border-rose-300',
      accent: 'rose'
    },
    organizationLabel: 'Salon & Wellness Spa',
    organizationPluralLabel: 'Salons & Spas',
    customerLabel: 'Guest / Client',
    customerPluralLabel: 'Guests & Clients',
    customerIdentifierLabel: 'Guest Member ID',
    customerNotesLabel: 'Skin / Hair Profile & Sensitivities',
    staffLabel: 'Master Stylist / Aesthetician',
    staffPluralLabel: 'Stylists & Aestheticians',
    appointmentLabel: 'Wellness Treatment',
    appointmentPluralLabel: 'Wellness Treatments',
    branchLabel: 'Salon / Studio Branch',
    branchPluralLabel: 'Salon & Spa Studios',
    serviceLabel: 'Beauty / Spa Treatment',
    servicePluralLabel: 'Spa & Salon Services',
    sampleBookingNotes: 'Guest booked hydro-facial treatment. Sensitive skin prone to redness; prefers organic botanical serums.',
    defaultWhatsAppTemplate: 'Greetings {customer_name}! Your luxury treatment {service_name} is reserved at {organization_name} ({branch_name}) for {appointment_date}. Specialist: {staff_name}.',
    sampleCustomerTags: ['VIP Member', 'Bridal Party', 'Organic Products Only', 'Frequent Guest', 'Skin Sensitivity'],
    servicePresets: [
      {
        name: 'Master Haircut & Keratin Treatment',
        category: 'Hair Care',
        duration_minutes: 60,
        price: 85,
        description: 'Precision shear cut, customized clarifying shampoo, organic keratin infusion, and blowout finish.'
      },
      {
        name: 'Holistic Spa & Aromatherapy Massage',
        category: 'Massage & Body',
        duration_minutes: 60,
        price: 110,
        description: 'Full-body Swedish pressure massage utilizing hot volcanic stones and bespoke organic essential oils.'
      },
      {
        name: 'Hydra-Facial & Skin Revitalisation',
        category: 'Skincare',
        duration_minutes: 50,
        price: 95,
        description: 'Vortex suction pore cleansing, glycolic peel extraction, and hyaluronic acid antioxidant serum infusion.'
      },
      {
        name: 'Deluxe Manicure & Pedicure Suite',
        category: 'Nails',
        duration_minutes: 45,
        price: 55,
        description: 'Dead sea salt exfoliation, paraffin wax treatment, cuticle restoration, and gel lacquer application.'
      }
    ]
  },

  legal: {
    id: 'legal',
    name: 'Strategic Management & Legal Advisory',
    sector: 'Consultancy',
    badgeColor: {
      bg: 'bg-slate-100 text-slate-800 border-slate-300',
      text: 'text-slate-800',
      border: 'border-slate-400',
      accent: 'slate'
    },
    organizationLabel: 'Legal Chambers / Firm',
    organizationPluralLabel: 'Chambers & Firms',
    customerLabel: 'Corporate Client',
    customerPluralLabel: 'Corporate Clients',
    customerIdentifierLabel: 'Case Matter / Retainer ID',
    customerNotesLabel: 'Case File & Privilege Retainer Notes',
    staffLabel: 'Senior Counsel / Partner',
    staffPluralLabel: 'Attorneys & Legal Partners',
    appointmentLabel: 'Legal Advisory Conference',
    appointmentPluralLabel: 'Legal Conferences',
    branchLabel: 'Chambers / Practice Office',
    branchPluralLabel: 'Practice Offices',
    serviceLabel: 'Legal & Strategic Service',
    servicePluralLabel: 'Legal & Strategic Services',
    sampleBookingNotes: 'Corporate cross-border acquisition review. Privileged discussion on regulatory clearance and antitrust filings.',
    defaultWhatsAppTemplate: 'Confidential Notice: {customer_name}, your legal advisory conference for {service_name} is arranged for {appointment_date} with Senior Counsel {staff_name} at {organization_name} ({branch_name}).',
    sampleCustomerTags: ['Corporate Retainer', 'M&A Deal', 'Litigation', 'Confidential Matter', 'Cross-Border'],
    servicePresets: [
      {
        name: 'Corporate Business Strategy Session',
        category: 'Corporate Strategy',
        duration_minutes: 60,
        price: 200,
        description: 'Market disruption analysis, enterprise valuation, board governance compliance, and capital structuring.'
      },
      {
        name: 'Legal Counsel & Contract Review',
        category: 'Commercial Law',
        duration_minutes: 60,
        price: 250,
        description: 'Comprehensive commercial agreement audit, indemnity clause drafting, liability shielding, and breach arbitration.'
      },
      {
        name: 'M&A Due Diligence Advisory',
        category: 'Transactions',
        duration_minutes: 90,
        price: 450,
        description: 'Target asset audit, vendor liability disclosures, regulatory filings verification, and closing escrow arrangements.'
      },
      {
        name: 'Intellectual Property & Patent Strategy',
        category: 'IP & Trademarks',
        duration_minutes: 60,
        price: 220,
        description: 'Global patent portfolio audit, trademark infringement clearance, and cross-licensing royalty agreements.'
      }
    ]
  },

  realestate: {
    id: 'realestate',
    name: 'Real Estate & Architecture Advisory',
    sector: 'Real Estate',
    badgeColor: {
      bg: 'bg-teal-50 text-teal-700 border-teal-200',
      text: 'text-teal-700',
      border: 'border-teal-300',
      accent: 'teal'
    },
    organizationLabel: 'Realty Agency / Firm',
    organizationPluralLabel: 'Realty Agencies',
    customerLabel: 'Buyer / Property Investor',
    customerPluralLabel: 'Buyers & Investors',
    customerIdentifierLabel: 'Client Listing ID',
    customerNotesLabel: 'Property Preferences & Budget Range',
    staffLabel: 'Realtor / Property Advisor',
    staffPluralLabel: 'Realtors & Brokers',
    appointmentLabel: 'Property Tour / Consultation',
    appointmentPluralLabel: 'Property Tours',
    branchLabel: 'Brokerage Office',
    branchPluralLabel: 'Brokerage Offices',
    serviceLabel: 'Property Advisory Service',
    servicePluralLabel: 'Realty & Advisory Services',
    sampleBookingNotes: 'Buyer seeking 3BHK penthouse with downtown skyline view. Pre-approved for $1.2M mortgage.',
    defaultWhatsAppTemplate: 'Hello {customer_name}, your property tour for {service_name} at {organization_name} ({branch_name}) is confirmed for {appointment_date} with Property Advisor {staff_name}. Note: {notes}.',
    sampleCustomerTags: ['Pre-Approved Buyer', 'Luxury Commercial', 'First-Time Buyer', 'Investor Portfolio', 'Immediate Possession'],
    servicePresets: [
      {
        name: 'VIP Property Tour & Site Inspection',
        category: 'Viewing',
        duration_minutes: 60,
        price: 75,
        description: 'Guided walkthrough of luxury residential units, architectural inspection, and neighborhood amenities briefing.'
      },
      {
        name: 'Commercial Lease & Zoning Consultation',
        category: 'Commercial',
        duration_minutes: 60,
        price: 150,
        description: 'Zoning ordinance review, tenant improvements allowance negotiation, and long-term lease indexing analysis.'
      },
      {
        name: 'Real Estate Valuation & Appraisal Review',
        category: 'Valuation',
        duration_minutes: 45,
        price: 120,
        description: 'Comparative market analysis (CMA), capitalization rate computation, and historical appraisal valuation.'
      }
    ]
  },

  custom: {
    id: 'custom',
    name: 'Custom Enterprise & Professional Services',
    sector: 'Professional Services',
    badgeColor: {
      bg: 'bg-violet-50 text-violet-700 border-violet-200',
      text: 'text-violet-700',
      border: 'border-violet-300',
      accent: 'violet'
    },
    organizationLabel: 'Enterprise / Firm',
    organizationPluralLabel: 'Enterprises & Firms',
    customerLabel: 'Client / Account',
    customerPluralLabel: 'Clients & Accounts',
    customerIdentifierLabel: 'Account ID / Reference',
    customerNotesLabel: 'Client Directives & Account Scope',
    staffLabel: 'Principal Consultant / Specialist',
    staffPluralLabel: 'Consultants & Specialists',
    appointmentLabel: 'Client Engagement / Session',
    appointmentPluralLabel: 'Client Engagements',
    branchLabel: 'Branch / Regional Office',
    branchPluralLabel: 'Regional Offices',
    serviceLabel: 'Professional Service Offering',
    servicePluralLabel: 'Service Offerings',
    sampleBookingNotes: 'Client booked quarterly executive review and operational workflow diagnostics.',
    defaultWhatsAppTemplate: 'Dear {customer_name}, your professional session for {service_name} is arranged on {appointment_date} with {staff_name} at {organization_name} ({branch_name}). Note: {notes}.',
    sampleCustomerTags: ['Enterprise Account', 'Retainer Agreement', 'Executive Review', 'High Priority', 'Active SLA'],
    servicePresets: [
      {
        name: 'Executive Consultation & Strategy Review',
        category: 'Consulting',
        duration_minutes: 60,
        price: 180,
        description: 'Senior stakeholder strategic alignment session, operational roadmap review, and milestone planning.'
      },
      {
        name: 'Technical Audit & Operations Review',
        category: 'Audit',
        duration_minutes: 90,
        price: 240,
        description: 'End-to-end process mapping, compliance benchmark evaluation, and efficiency optimization recommendations.'
      },
      {
        name: 'Bespoke Advisory Engagement',
        category: 'Advisory',
        duration_minutes: 45,
        price: 130,
        description: 'Dedicated tailored consultation addressing specific client requirements and actionable deliverables.'
      }
    ]
  }
};

/**
 * Normalizes an arbitrary industry template or sector string into a known config key.
 */
export function normalizeIndustryKey(str?: string | null): string {
  if (!str) return 'healthcare';
  const s = str.toLowerCase();
  if (s.includes('health') || s.includes('medic') || s.includes('clinic') || s.includes('hospital') || s.includes('dental')) {
    return 'healthcare';
  }
  if (s.includes('wealth') || s.includes('finan') || s.includes('asset') || s.includes('invest') || s.includes('bank')) {
    return 'finance';
  }
  if (s.includes('retail') || s.includes('styl') || s.includes('fashion') || s.includes('boutique') || s.includes('couture')) {
    return 'retail';
  }
  if (s.includes('insur') || s.includes('risk') || s.includes('policy') || s.includes('underwrit')) {
    return 'insurance';
  }
  if (s.includes('counsel') || s.includes('academ') || s.includes('univers') || s.includes('school') || s.includes('educat')) {
    return 'education';
  }
  if (s.includes('salon') || s.includes('spa') || s.includes('aesthetic') || s.includes('beauty') || s.includes('wellness')) {
    return 'salon';
  }
  if (s.includes('legal') || s.includes('law') || s.includes('consult') || s.includes('strateg') || s.includes('attorney')) {
    return 'legal';
  }
  if (s.includes('real') || s.includes('estate') || s.includes('property') || s.includes('realty') || s.includes('architect')) {
    return 'realestate';
  }
  if (s.includes('custom') || s.includes('enterpris') || s.includes('profession') || s.includes('generic')) {
    return 'custom';
  }
  return 'healthcare';
}

/**
 * Retrieves the full IndustryConfig given a template name, sector, or ID.
 */
export function getIndustryConfig(industryTemplateOrSector?: string | null): IndustryConfig {
  const key = normalizeIndustryKey(industryTemplateOrSector);
  return (INDUSTRY_CONFIGS[key] || INDUSTRY_CONFIGS['healthcare']) as IndustryConfig;
}

/**
 * Quick access to terminology strings for clean dynamic UI interpolation.
 */
export function getIndustryTerms(industryTemplateOrSector?: string | null) {
  const config = getIndustryConfig(industryTemplateOrSector);
  const categories = Array.from(new Set(config.servicePresets.map(s => s.category)));

  return {
    organizationLabel: config.organizationLabel,
    organizationPluralLabel: config.organizationPluralLabel,
    organizationType: config.organizationLabel,
    customerLabel: config.customerLabel,
    customerPluralLabel: config.customerPluralLabel,
    customerSingular: config.customerLabel,
    customerPlural: config.customerPluralLabel,
    customerIdentifierLabel: config.customerIdentifierLabel,
    customerNotesLabel: config.customerNotesLabel,
    staffLabel: config.staffLabel,
    staffPluralLabel: config.staffPluralLabel,
    staffSingular: config.staffLabel,
    staffPlural: config.staffPluralLabel,
    appointmentLabel: config.appointmentLabel,
    appointmentPluralLabel: config.appointmentPluralLabel,
    appointmentSingular: config.appointmentLabel,
    appointmentPlural: config.appointmentPluralLabel,
    bookingSingular: config.appointmentLabel,
    bookingPlural: config.appointmentPluralLabel,
    branchLabel: config.branchLabel,
    branchPluralLabel: config.branchPluralLabel,
    branchSingular: config.branchLabel,
    branchPlural: config.branchPluralLabel,
    serviceLabel: config.serviceLabel,
    servicePluralLabel: config.servicePluralLabel,
    serviceSingular: config.serviceLabel,
    servicePlural: config.servicePluralLabel,
    serviceCategories: categories.length > 0 ? categories : ['General', 'Consultation', 'Premium'],
    sampleBookingNotes: config.sampleBookingNotes,
    defaultWhatsAppTemplate: config.defaultWhatsAppTemplate,
    sampleCustomerTags: config.sampleCustomerTags,
    servicePresets: config.servicePresets,
    defaultServices: config.servicePresets,
    badgeColor: config.badgeColor,
    badgeClass: typeof config.badgeColor === 'string' ? config.badgeColor : `${config.badgeColor.bg}`,
    badgeColorClass: typeof config.badgeColor === 'string' ? config.badgeColor : `${config.badgeColor.bg}`,
    name: config.name,
    sector: config.sector,
    description: `${config.name} tailored configuration with ${config.servicePresets.length} curated offerings.`,
    customFields: getIndustryCustomFields(industryTemplateOrSector),
    infoMessages: getIndustryInfoMessages(industryTemplateOrSector)
  };
}

export {
  getIndustryCustomFields,
  getIndustryInfoMessages,
  getDefaultIndustryCustomFields,
  formatIndustryCustomFieldsSummary,
  type IndustryCustomFieldDef,
  type IndustryInfoMessagePreset
} from './industry-custom-data';

export function getSectorTemplate(industryTemplateOrSector?: string | null) {
  const config = getIndustryConfig(industryTemplateOrSector);
  return {
    ...config,
    defaultServices: config.servicePresets,
    description: `${config.name} tailored catalog`
  };
}

export function getIndustryWhatsAppDefaults(industryTemplateOrSector?: string | null) {
  const terms = getIndustryTerms(industryTemplateOrSector);
  const topServices = terms.servicePresets.slice(0, 4).map((s, idx) => `${idx + 1}. *${s.name}* ($${s.price} • ${s.duration_minutes}m)`).join('\n');

  let prepText = `Please bring a valid Government Photo ID. Please arrive 10 minutes prior to your scheduled time.`;
  if (terms.sector === 'Healthcare') {
    prepText = `Please bring: 1) Valid Photo ID, 2) Health Insurance Card, 3) Recent lab or clinical records, 4) Current medication list. If fasting test is required, drink only water for 8 hours prior.`;
  } else if (terms.sector === 'Finance') {
    prepText = `Please have available: 1) Identification & KYC documentation, 2) Recent portfolio statements & asset summaries, 3) Preliminary financial objectives & tax filing records.`;
  } else if (terms.sector === 'Luxury Retail') {
    prepText = `Complimentary private fitting suite & refreshment bar reserved for your session. Feel free to bring wardrobe inspiration or specific tailoring garments.`;
  } else if (terms.sector === 'Insurance') {
    prepText = `Please prepare: 1) Valid ID & proof of residency, 2) Existing policy documents, 3) Asset appraisal or beneficiary details.`;
  } else if (terms.sector === 'Education') {
    prepText = `Please bring: 1) Academic transcripts, 2) Standardized test scores (SAT/ACT/IELTS/GRE if applicable), 3) Extracurricular resume or preliminary university wishlist.`;
  } else if (terms.sector === 'Salon & Wellness') {
    prepText = `Please arrive 10 minutes before your ritual. Wear comfortable attire. Inform your aesthetician of any skin sensitivities, allergies, or recent dermatological treatments.`;
  } else if (terms.sector === 'Legal') {
    prepText = `Confidential Attorney-Client consultation. Please prepare: 1) Chronology of events or corporate summary, 2) Existing contracts or disputed documents, 3) Questions for Senior Counsel.`;
  }

  return {
    welcomeMessage: `👋 Hello {customer_name}! Welcome to *{organization_name}* (${terms.name}). We are pleased to assist you with your ${terms.appointmentSingular.toLowerCase()}.\n\nReply with a number below to proceed:\n1️⃣ *Book ${terms.appointmentSingular}*\n2️⃣ *Service Catalog & Fee Schedule*\n3️⃣ *Branch Locations & Timings*\n4️⃣ *Required Documents & Prep Guide*\n5️⃣ *Speak with Front Desk Staff*`,
    infoCatalog: `📋 *{organization_name} — Curated Services & Fee Schedule*\n\n${topServices}\n\n💡 All sessions include dedicated 1-on-1 consultation with our licensed ${terms.staffSingular.toLowerCase()}.\nReply *1* to pick a slot or send a service name!`,
    infoLocation: `📍 *{organization_name} — Branch Locations & Operating Hours*\n\n• *Main Executive Branch*: 742 Evergreen Terrace (Mon-Sat 08:30 AM - 07:00 PM)\n• *Downtown Satellite Office*: 100 Market St, Suite 500 (Mon-Fri 09:00 AM - 06:00 PM)\n\n🚗 *Visitor Parking:* Complimentary guest parking on premises. Wheelchair accessible.`,
    infoPreparation: `📝 *{organization_name} — Pre-Visit Preparation & Required Documents*\n\n${prepText}`,
    bookingInstructions: `To schedule via WhatsApp, reply *1* now, or click your direct booking link: https://appointocare.com/book?org={organization_code}`
  };
}

export const ALL_INDUSTRY_TEMPLATES = Object.values(INDUSTRY_CONFIGS);
