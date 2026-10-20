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
  leftPercent: number;
  size: number;
  color: string;
  gradient: string;
  durationSec: number;
  delaySec: number;
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

  // Interactive Liquid Press Ripples
  ripples: LiquidRipple[] = [];

  // Interactive Falling & Poppable Balloons
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

    // Start streaming interactive descending balloons
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
  // Interactive Liquid Press Anywhere on Page
  // =========================================================================
  onPageClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    // Don't trigger liquid ripple if clicking directly on a balloon (handled by popBalloon)
    if (target && target.closest('.balloon-item')) {
      return;
    }

    const ripple: LiquidRipple = {
      id: Date.now() + Math.random(),
      x: event.clientX,
      y: event.clientY
    };
    this.ripples.push(ripple);
    this.playLiquidPressSound();

    setTimeout(() => {
      this.ripples = this.ripples.filter(r => r.id !== ripple.id);
    }, 850);
  }

  private playLiquidPressSound(): void {
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

      // Soft water droplet press tone
      osc.type = 'sine';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(540, now + 0.08);

      gain.gain.setValueAtTime(0.045, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start(now);
      osc.stop(now + 0.08);
    } catch {}
  }

  // =========================================================================
  // Interactive Descending Balloons with Popping Mechanics
  // =========================================================================
  private startBalloonStream(): void {
    // Initial staggered balloons
    for (let i = 0; i < 4; i++) {
      this.spawnBalloon(true);
    }

    // Continuously spawn descending balloons from top
    this.balloonInterval = setInterval(() => {
      if (this.balloons.length < 10) {
        this.spawnBalloon(false);
      }
    }, 2400);
  }

  private spawnBalloon(initialSpread: boolean = false): void {
    const themes = [
      { color: '#ec4899', gradient: 'radial-gradient(circle at 35% 28%, #f472b6 0%, #db2777 55%, #9d174d 100%)' },
      { color: '#38bdf8', gradient: 'radial-gradient(circle at 35% 28%, #7dd3fc 0%, #0284c7 55%, #0369a1 100%)' },
      { color: '#a855f7', gradient: 'radial-gradient(circle at 35% 28%, #c084fc 0%, #9333ea 55%, #6b21a8 100%)' },
      { color: '#10b981', gradient: 'radial-gradient(circle at 35% 28%, #34d399 0%, #059669 55%, #065f46 100%)' },
      { color: '#f59e0b', gradient: 'radial-gradient(circle at 35% 28%, #fbbf24 0%, #d97706 55%, #92400e 100%)' },
      { color: '#6366f1', gradient: 'radial-gradient(circle at 35% 28%, #818cf8 0%, #4f46e5 55%, #3730a3 100%)' },
      { color: '#f43f5e', gradient: 'radial-gradient(circle at 35% 28%, #fb7185 0%, #e11d48 55%, #9f1239 100%)' }
    ];

    const chosenTheme = themes[Math.floor(Math.random() * themes.length)];
    const size = Math.floor(Math.random() * 20) + 48; // 48px to 68px
    const leftPercent = Math.floor(Math.random() * 88) + 6; // 6% to 94%
    const durationSec = Math.floor(Math.random() * 5) + 12; // 12s to 17s
    const delaySec = initialSpread ? Math.random() * -8 : 0;

    const balloon: InteractiveBalloon = {
      id: Date.now() + Math.random(),
      leftPercent,
      size,
      color: chosenTheme.color,
      gradient: chosenTheme.gradient,
      durationSec,
      delaySec,
      popping: false
    };

    this.balloons.push(balloon);

    // Clean up when descent completes
    setTimeout(() => {
      this.balloons = this.balloons.filter(b => b.id !== balloon.id);
    }, (durationSec + 2) * 1000);
  }

  popBalloon(balloon: InteractiveBalloon, event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault();

    if (balloon.popping) return;
    balloon.popping = true;

    this.playPopSound();
    this.poppedBalloonCount++;

    // Celebratory score label at pop position
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
    }, 900);

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
      osc.frequency.setValueAtTime(620, now);
      osc.frequency.exponentialRampToValueAtTime(130, now + 0.08);

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
