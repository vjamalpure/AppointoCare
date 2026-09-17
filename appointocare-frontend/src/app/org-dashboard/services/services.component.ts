import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../services/platform.service';
import { IndustryService } from '../../services/industry.service';
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
  selectedSector = 'ALL';
  searchTerm = '';
  loading = false;
  importingSector = false;

  // Add/Edit Dialog
  showDialog = false;
  isEditMode = false;
  currentService: any = {
    name: '',
    category: 'Consultation',
    price: 60,
    duration_minutes: 30,
    active: true,
    sector: 'Healthcare'
  };

  selectedTemplateToImport = 'Healthcare';

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
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const orgSector = this.industryService.getSector();
    if (orgSector) {
      this.selectedTemplateToImport = orgSector;
      this.currentService.sector = orgSector;
    }
    this.loadServices();
    this.loadTemplates();
  }

  loadServices(): void {
    this.loading = true;
    this.platform.getServices().subscribe({
      next: (data) => {
        this.services = data;
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
        this.sectorTemplates = data;
      }
    });
  }

  applyFilter(): void {
    let list = [...this.services];

    if (this.selectedSector !== 'ALL') {
      list = list.filter(s => (s.sector || '').toLowerCase() === this.selectedSector.toLowerCase());
    }

    if (this.searchTerm.trim()) {
      const q = this.searchTerm.toLowerCase();
      list = list.filter(s =>
        s.name.toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q)
      );
    }

    this.filteredServices = list;
  }

  openCreateDialog(): void {
    this.isEditMode = false;
    const orgSector = this.industryService.getSector();
    this.currentService = {
      name: '',
      category: 'General Service',
      price: 50,
      duration_minutes: 30,
      active: true,
      sector: orgSector || 'Healthcare'
    };
    this.showDialog = true;
  }

  openEditDialog(service: any, event: Event): void {
    event.stopPropagation();
    this.isEditMode = true;
    this.currentService = { ...service };
    this.showDialog = true;
  }

  saveService(): void {
    if (!this.currentService.name || !this.currentService.price) {
      this.snackBar.open('Please fill in service name and price', 'Dismiss', { duration: 2500 });
      return;
    }

    if (this.isEditMode) {
      this.platform.updateService(this.currentService.id, this.currentService).subscribe({
        next: () => {
          this.snackBar.open('Service updated successfully', 'Dismiss', { duration: 2500 });
          this.showDialog = false;
          this.loadServices();
        }
      });
    } else {
      this.platform.createService(this.currentService).subscribe({
        next: () => {
          this.snackBar.open('Service added to catalog', 'Dismiss', { duration: 2500 });
          this.showDialog = false;
          this.loadServices();
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
}
