import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../auth.service';
import { IndustryService } from '../../services/industry.service';
import { Router } from '@angular/router';
import { NgForm } from '@angular/forms';

export interface SampleCredential {
  title: string;
  role: 'organization' | 'staff' | 'superadmin';
  roleBadge: string;
  code: string;
  user: string;
  pass: string;
  desc: string;
  sector?: string;
}

export interface LiquidRipple {
  id: number;
  x: number;
  y: number;
}

export interface InteractiveBalloon {
  id: number;
  uid: string;
  leftPercent: number;
  width: number;
  height: number;
  color: string;
  lightColor: string;
  midColor: string;
  darkColor: string;
  durationSec: number;
  delaySec: number;
  swayDuration: number;
  popping?: boolean;
}

export interface PopEffect {
  id: number;
  x: number;
  y: number;
  color: string;
  label: string;
}

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit, OnDestroy {
  organization_code = 'ORG1';
  username = 'org1';
  password = 'Org@12345';
  rememberMe = true;
  loading = false;
  errorMsg = '';
  showPassword = false;

  selectedRole: 'organization' | 'staff' | 'superadmin' = 'organization';
  currentYear: number = new Date().getFullYear();

  // Dark / Night Mode Support (Single floating moon toggle on showcase)
  isDarkMode = false;

  // Modals & Popups
  showCredentialsModal = false;
  activeInfoModal: 'integrations' | 'license' | 'terms' | 'blog' | 'register' | 'features' | null = null;
  copyToastMsg = '';
  private toastTimer: any = null;

  // Minimal Organic Liquid Press (Visual only, silent)
  ripples: LiquidRipple[] = [];

  // Interactive Flowing Balloons with Realistic Latex Shapes & Diverse Sizes
  balloons: InteractiveBalloon[] = [];
  popEffects: PopEffect[] = [];
  poppedBalloonCount = 0;
  private balloonInterval: any = null;
  private audioCtx: any = null;

  // New Demo Registration Form State
  registerData = {
    clinicName: '',
    ownerName: '',
    email: '',
    sector: 'Healthcare',
    phone: '',
    submitted: false
  };

  sampleCredentials: SampleCredential[] = [
    {
      title: 'Platform SuperAdmin',
      role: 'superadmin',
      roleBadge: 'SuperAdmin Master',
      code: '',
      user: 'superadmin',
      pass: 'Admin@12345',
      desc: 'Master platform controls, analytics, multi-tenant governance & audit.'
    },
    {
      title: 'Healthcare Clinic Admin (ORG1)',
      role: 'organization',
      roleBadge: 'Clinic Owner / Admin',
      code: 'ORG1',
      user: 'org1',
      pass: 'Org@12345',
      desc: 'City Care Health & Dental: services, staff schedules, patients & billing.',
      sector: 'Healthcare'
    },
    {
      title: 'Dr. Sarah (Clinical Specialist)',
      role: 'staff',
      roleBadge: 'Doctor / Specialist',
      code: 'ORG1',
      user: 'doc_sarah',
      pass: 'Staff@12345',
      desc: 'Chief Surgeon / Specialist schedule, active bookings & consult notes.',
      sector: 'Healthcare'
    },
    {
      title: 'Aesthetics & Wellness Spa (ORG2)',
      role: 'organization',
      roleBadge: 'Salon & Spa Admin',
      code: 'ORG2',
      user: 'org2',
      pass: 'Org@12345',
      desc: 'Apex Aesthetics Spa: stylist bookings, formulation lookbooks & packages.',
      sector: 'Salon'
    },
    {
      title: 'Vanguard Wealth Advisory (ORG3)',
      role: 'organization',
      roleBadge: 'Finance & Wealth Admin',
      code: 'ORG3',
      user: 'org3',
      pass: 'Org@12345',
      desc: 'Financial advisory client consultations, retainer ledgers & reviews.',
      sector: 'Finance'
    }
  ];

  constructor(
    private auth: AuthService,
    private industry: IndustryService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const savedTheme = localStorage.getItem('appointocare_theme');
    this.isDarkMode = savedTheme === 'dark';

    // Start streaming diverse, realistic flowing balloons
    this.startBalloonStream();
  }

  ngOnDestroy(): void {
    if (this.balloonInterval) {
      clearInterval(this.balloonInterval);
    }
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
  }

  // =========================================================================
  // Minimal Liquid Press anywhere on page (Pure fluid visual, silent)
  // =========================================================================
  onPageClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    // Don't trigger liquid ripple if clicking directly on a balloon
    if (target && target.closest('.balloon-item')) {
      return;
    }

    const ripple: LiquidRipple = {
      id: Date.now() + Math.random(),
      x: event.clientX,
      y: event.clientY
    };
    this.ripples.push(ripple);

    setTimeout(() => {
      this.ripples = this.ripples.filter(r => r.id !== ripple.id);
    }, 480);
  }

  // =========================================================================
  // Realistic Balloons (Diverse sizes from mini to jumbo, teardrop shape)
  // =========================================================================
  private startBalloonStream(): void {
    // Immediate staggered balloons floating at various heights across screen
    const initialDelays = [-1.5, -4.5, -7.5, -10.5, -3.0, -6.0];
    for (const delay of initialDelays) {
      this.spawnBalloon(delay);
    }

    // Continuously spawn fresh balloons of varied sizes
    this.balloonInterval = setInterval(() => {
      if (this.balloons.length < 14) {
        this.spawnBalloon(0);
      }
    }, 1900);
  }

  private spawnBalloon(delaySec: number = 0): void {
    const themes = [
      // Crimson Ruby
      { color: '#e11d48', lightColor: '#fda4af', midColor: '#f43f5e', darkColor: '#881337' },
      // Azure Sky
      { color: '#0284c7', lightColor: '#7dd3fc', midColor: '#0ea5e9', darkColor: '#0369a1' },
      // Royal Indigo
      { color: '#4f46e5', lightColor: '#a5b4fc', midColor: '#6366f1', darkColor: '#312e81' },
      // Electric Purple
      { color: '#9333ea', lightColor: '#d8b4fe', midColor: '#a855f7', darkColor: '#581c87' },
      // Emerald Mint
      { color: '#059669', lightColor: '#6ee7b7', midColor: '#10b981', darkColor: '#064e3b' },
      // Sunset Tangerine
      { color: '#ea580c', lightColor: '#fdba74', midColor: '#f97316', darkColor: '#7c2d12' },
      // Vibrant Fuchsia
      { color: '#db2777', lightColor: '#f472b6', midColor: '#ec4899', darkColor: '#831843' },
      // Solar Gold
      { color: '#d97706', lightColor: '#fde047', midColor: '#f59e0b', darkColor: '#78350f' },
      // Cyan Lagoon
      { color: '#0891b2', lightColor: '#67e8f9', midColor: '#06b6d4', darkColor: '#164e63' }
    ];

    const chosenTheme = themes[Math.floor(Math.random() * themes.length)];

    // Distinct Size Tiers: Each balloon has a visibly different size!
    const sizeTiers = [
      { minW: 36, maxW: 46, ratio: 1.34 }, // Petite / Mini
      { minW: 52, maxW: 66, ratio: 1.30 }, // Medium / Standard
      { minW: 74, maxW: 90, ratio: 1.28 }, // Large
      { minW: 98, maxW: 118, ratio: 1.26 } // Jumbo
    ];
    const tier = sizeTiers[Math.floor(Math.random() * sizeTiers.length)];
    const width = Math.floor(Math.random() * (tier.maxW - tier.minW + 1)) + tier.minW;
    const height = Math.round(width * tier.ratio);

    const leftPercent = Math.floor(Math.random() * 86) + 7; // 7% to 93%
    const durationSec = Math.floor(Math.random() * 5) + 12; // 12s to 16s
    const swayDuration = Math.random() * 1.5 + 2.6; // 2.6s to 4.1s
    const uid = Math.random().toString(36).substring(2, 9);

    const balloon: InteractiveBalloon = {
      id: Date.now() + Math.random(),
      uid,
      leftPercent,
      width,
      height,
      color: chosenTheme.color,
      lightColor: chosenTheme.lightColor,
      midColor: chosenTheme.midColor,
      darkColor: chosenTheme.darkColor,
      durationSec,
      delaySec,
      swayDuration,
      popping: false
    };

    this.balloons.push(balloon);

    // Auto clean up after fall completes
    const remainingTimeMs = Math.max(2000, (durationSec + delaySec + 2) * 1000);
    setTimeout(() => {
      this.balloons = this.balloons.filter(b => b.id !== balloon.id);
    }, remainingTimeMs);
  }

  // Sound triggers ONLY on popping balloons
  popBalloon(balloon: InteractiveBalloon, event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault();

    if (balloon.popping) return;
    balloon.popping = true;

    // Play crisp realistic pop sound
    this.playPopSound();
    this.poppedBalloonCount++;

    // Floating celebratory score badge
    const popEffect: PopEffect = {
      id: Date.now() + Math.random(),
      x: event.clientX,
      y: event.clientY,
      color: balloon.color,
      label: this.poppedBalloonCount % 5 === 0 ? '✨ Combo! 🎈' : '+1 🎈'
    };
    this.popEffects.push(popEffect);

    setTimeout(() => {
      this.popEffects = this.popEffects.filter(p => p.id !== popEffect.id);
    }, 850);

    setTimeout(() => {
      this.balloons = this.balloons.filter(b => b.id !== balloon.id);
    }, 280);
  }

  private playPopSound(): void {
    try {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtxClass) return;
      if (!this.audioCtx) {
        this.audioCtx = new AudioCtxClass();
      }
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      const now = this.audioCtx.currentTime;

      // Realistic crisp pitch drop pop
      osc.type = 'sine';
      osc.frequency.setValueAtTime(660, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.08);

      gain.gain.setValueAtTime(0.35, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start(now);
      osc.stop(now + 0.08);
    } catch {}
  }

  // =========================================================================
  // Theme & Auth Controls
  // =========================================================================
  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
    localStorage.setItem('appointocare_theme', this.isDarkMode ? 'dark' : 'light');
    this.showToast(this.isDarkMode ? '🌙 Night mode activated' : '☀️ Day mode activated');
  }

  setRole(role: 'organization' | 'staff' | 'superadmin'): void {
    this.selectedRole = role;
    this.errorMsg = '';
    if (role === 'superadmin') {
      this.username = 'superadmin';
      this.password = 'Admin@12345';
      this.organization_code = '';
    } else if (role === 'organization') {
      this.username = 'org1';
      this.password = 'Org@12345';
      this.organization_code = 'ORG1';
    } else if (role === 'staff') {
      this.username = 'doc_sarah';
      this.password = 'Staff@12345';
      this.organization_code = 'ORG1';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  clearError(): void {
    this.errorMsg = '';
  }

  toggleCredentialsModal(open?: boolean): void {
    this.showCredentialsModal = open !== undefined ? open : !this.showCredentialsModal;
  }

  openInfoModal(modalType: 'integrations' | 'license' | 'terms' | 'blog' | 'register' | 'features'): void {
    this.activeInfoModal = modalType;
  }

  closeInfoModal(): void {
    this.activeInfoModal = null;
  }

  handleRegisterSubmit(): void {
    if (!this.registerData.clinicName || !this.registerData.email) return;
    this.registerData.submitted = true;
    setTimeout(() => {
      this.showToast('✓ Demo workspace created! Please sign in with sample credentials.');
      this.closeInfoModal();
      this.registerData.submitted = false;
      this.setRole('organization');
    }, 1200);
  }

  copyAndApply(cred: SampleCredential): void {
    this.selectedRole = cred.role;
    this.username = cred.user;
    this.password = cred.pass;
    this.organization_code = cred.code;
    this.errorMsg = '';

    if (cred.sector) {
      this.industry.setSector(cred.sector);
    }

    const copyText = cred.role === 'superadmin'
      ? `Username: ${cred.user} | Password: ${cred.pass}`
      : `Org Code: ${cred.code} | Username: ${cred.user} | Password: ${cred.pass}`;

    this.copyToClipboard(copyText);
    this.showToast(`✓ Copied ${cred.title} credentials and filled into form!`);
    this.showCredentialsModal = false;
  }

  copyToClipboard(text: string): void {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => {
        this.fallbackCopy(text);
      });
    } else {
      this.fallbackCopy(text);
    }
  }

  private fallbackCopy(text: string): void {
    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.style.position = 'fixed';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    } catch {}
  }

  private showToast(msg: string): void {
    this.copyToastMsg = msg;
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
    }
    this.toastTimer = setTimeout(() => {
      this.copyToastMsg = '';
    }, 3500);
  }

  onSubmit(loginForm: NgForm): void {
    if (!loginForm.valid) return;

    this.loading = true;
    this.errorMsg = '';

    const cleanUsername = this.username?.trim();
    const cleanPassword = this.password;
    const orgCode = this.selectedRole === 'superadmin' ? undefined : (this.organization_code?.trim() || undefined);

    this.auth.login(cleanUsername, cleanPassword, orgCode, this.rememberMe)
      .subscribe({
        next: (res: any) => {
          if (!res?.access_token) {
            this.errorMsg = 'Invalid response from server';
            this.loading = false;
            return;
          }

          if (res?.organization_name) {
            this.auth.saveOrgName(res.organization_name, this.rememberMe);
          }
          if (res?.sector) {
            this.auth.saveSector(res.sector, this.rememberMe);
            this.industry.setSector(res.sector);
          }

          const role = this.auth.getUserRole();
          if (role === 'Admin' || role === 'SuperAdmin') {
            this.router.navigate(['/admin-dashboard']);
          } else {
            this.router.navigate(['/org-dashboard']);
          }
        },
        error: (err) => {
          this.errorMsg = err?.error?.msg || 'Invalid credentials or login failed';
          this.loading = false;
        },
        complete: () => {
          this.loading = false;
        }
      });
  }
}
