import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { IndustryService } from '../../services/industry.service';
import { AuthService } from '../../auth/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-org-services',
  templateUrl: './services.component.html',
  styleUrls: ['./services.component.scss']
})
export class ServicesComponent implements OnInit {
  services: any[] = [];
  filteredServices: any[] = [];
  sectorTemplates: any[] = [];
  categories: string[] = [];

  isSuperAdmin = false;
  orgSector = 'Healthcare';
  orgName = '';

  selectedSector = 'ALL';
  selectedCategory = 'ALL';
  selectedStatus = 'ALL';
  searchTerm = '';

  loading = false;
  isSaving = false;
  importingSector = false;

  // Add/Edit Dialog
  showDialog = false;
  isEditMode = false;
  currentService: any = {
    name: '',
    category: 'Consultation',
    price: 500,
    duration_minutes: 30,
    active: true,
    sector: 'Healthcare',
    description: '',
    organization_id: null
  };

  selectedTemplateToImport = 'Healthcare';

  // Available sectors for SuperAdmin view only
  sectors = [
    { label: 'All Sectors', value: 'ALL' },
    { label: 'Healthcare & Clinic', value: 'Healthcare' },
    { label: 'Wealth & Financial Advisory', value: 'Finance' },
    { label: 'Salon & Wellness Spa', value: 'Salon' },
    { label: 'Luxury Retail & Styling', value: 'Retail' },
    { label: 'Life & General Insurance', value: 'Insurance' },
    { label: 'Academy & University Counseling', value: 'Education' },
    { label: 'Legal & Management Consulting', value: 'Consultancy' },
    { label: 'Real Estate & Architecture', value: 'Real Estate' },
    { label: 'Enterprise Consulting Solutions', value: 'Professional Services' }
  ];

  constructor(
    private platform: PlatformService,
    public industryService: IndustryService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const role = this.authService.getUserRole();
    this.isSuperAdmin = role === 'Admin' || role === 'SuperAdmin';
    this.orgSector = this.industryService.getSector() || this.authService.getSector() || 'Healthcare';
    this.orgName = this.authService.getOrganizationName() || '';

    this.selectedTemplateToImport = this.orgSector;
    this.currentService.sector = this.orgSector;

    this.loadServices();
    if (this.isSuperAdmin) {
      this.loadTemplates();
    }
  }

  loadServices(): void {
    this.loading = true;
    this.platform.getServices().subscribe({
      next: (data) => {
        this.services = data || [];
        const catSet = new Set<string>();
        for (const s of this.services) {
          if (s.category && s.category.trim()) {
            catSet.add(s.category.trim());
          }
        }
        this.categories = Array.from(catSet);
        this.applyFilter();
        this.loading = false;
      },
      error: () => {
        this.snackBar.open('Failed to load services catalog', 'Dismiss', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  loadTemplates(): void {
    this.platform.getTemplates().subscribe({
      next: (data) => {
        this.sectorTemplates = data || [];
      }
    });
  }

  applyFilter(): void {
    let list = [...this.services];

    if (this.isSuperAdmin) {
      if (this.selectedSector !== 'ALL') {
        list = list.filter(s => (s.sector || '').toLowerCase() === this.selectedSector.toLowerCase());
      }
    } else {
      // Organization view: Filter by category
      if (this.selectedCategory !== 'ALL') {
        list = list.filter(s => (s.category || '').toLowerCase() === this.selectedCategory.toLowerCase());
      }
    }

    if (this.selectedStatus === 'ACTIVE') {
      list = list.filter(s => s.active);
    } else if (this.selectedStatus === 'INACTIVE') {
      list = list.filter(s => !s.active);
    }

    if (this.searchTerm.trim()) {
      const q = this.searchTerm.toLowerCase();
      list = list.filter(s =>
        (s.name || '').toLowerCase().includes(q) ||
        (s.category || '').toLowerCase().includes(q) ||
        (s.description || '').toLowerCase().includes(q)
      );
    }

    this.filteredServices = list;
  }

  openCreateDialog(): void {
    this.isEditMode = false;
    const orgId = this.authService.getOrganizationId();
    this.currentService = {
      name: '',
      category: this.categories.length ? this.categories[0] : 'Consultation',
      price: 500,
      duration_minutes: 30,
      active: true,
      sector: this.orgSector || 'Healthcare',
      description: '',
      organization_id: orgId ? parseInt(orgId, 10) : undefined
    };
    this.showDialog = true;
  }

  openEditDialog(service: any, event: Event): void {
    event.stopPropagation();
    this.isEditMode = true;
    this.currentService = {
      ...service,
      sector: service.sector || this.orgSector,
      description: service.description || ''
    };
    this.showDialog = true;
  }

  saveService(): void {
    if (!this.currentService.name || !this.currentService.name.trim()) {
      this.snackBar.open('Please enter a service name', 'Dismiss', { duration: 2500 });
      return;
    }

    if (this.currentService.price === null || this.currentService.price === undefined || this.currentService.price < 0) {
      this.snackBar.open('Please enter a valid price (>= 0)', 'Dismiss', { duration: 2500 });
      return;
    }

    if (!this.isSuperAdmin) {
      this.currentService.sector = this.orgSector;
    }

    const orgId = this.authService.getOrganizationId();
    if (orgId && !this.currentService.organization_id) {
      this.currentService.organization_id = parseInt(orgId, 10);
    }

    this.isSaving = true;

    if (this.isEditMode) {
      this.platform.updateService(this.currentService.id, this.currentService).subscribe({
        next: () => {
          this.snackBar.open('Service updated successfully', 'Dismiss', { duration: 2500 });
          this.isSaving = false;
          this.showDialog = false;
          this.loadServices();
        },
        error: (err) => {
          this.isSaving = false;
          this.snackBar.open(err?.error?.msg || 'Failed to update service', 'Dismiss', { duration: 3500 });
        }
      });
    } else {
      this.platform.createService(this.currentService).subscribe({
        next: () => {
          this.snackBar.open('Service added to catalog successfully', 'Dismiss', { duration: 2500 });
          this.isSaving = false;
          this.showDialog = false;
          this.loadServices();
        },
        error: (err) => {
          this.isSaving = false;
          this.snackBar.open(err?.error?.msg || 'Failed to create service', 'Dismiss', { duration: 3500 });
        }
      });
    }
  }

  toggleActive(service: any, event: Event): void {
    event.stopPropagation();
    const updated = !service.active;
    this.platform.updateService(service.id, { active: updated }).subscribe({
      next: () => {
        service.active = updated;
        this.snackBar.open(`Service marked as ${updated ? 'Active' : 'Disabled'}`, 'Dismiss', { duration: 2000 });
        this.applyFilter();
      },
      error: () => {
        this.snackBar.open('Failed to update service status', 'Dismiss', { duration: 2000 });
      }
    });
  }

  deleteService(id: number, event: Event): void {
    event.stopPropagation();
    if (confirm('Delete this service from the catalog?')) {
      this.platform.deleteService(id).subscribe({
        next: () => {
          this.snackBar.open('Service deleted', 'Dismiss', { duration: 2000 });
          this.loadServices();
        },
        error: (err) => {
          this.snackBar.open(err?.error?.msg || 'Failed to delete service', 'Dismiss', { duration: 3000 });
        }
      });
    }
  }

  importTemplate(): void {
    this.importingSector = true;
    this.platform.importSectorTemplate(this.selectedTemplateToImport).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg || 'Sector services imported successfully!', 'Dismiss', { duration: 3500 });
        this.importingSector = false;
        this.loadServices();
      },
      error: () => {
        this.snackBar.open('Failed to import sector template', 'Dismiss', { duration: 3000 });
        this.importingSector = false;
      }
    });
  }

  importOwnSectorTemplate(): void {
    this.importingSector = true;
    this.platform.importSectorTemplate(this.orgSector).subscribe({
      next: (res) => {
        this.snackBar.open(res.msg || `${this.orgSector} starter services loaded successfully!`, 'Dismiss', { duration: 3500 });
        this.importingSector = false;
        this.loadServices();
      },
      error: (err) => {
        this.snackBar.open(err?.error?.msg || 'Failed to load templates', 'Dismiss', { duration: 3000 });
        this.importingSector = false;
      }
    });
  }
}
