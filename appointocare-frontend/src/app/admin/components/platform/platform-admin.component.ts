import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../../services/platform.service';

@Component({
  selector: 'app-platform-admin',
  templateUrl: './platform-admin.component.html',
  styleUrls: ['./platform-admin.component.scss']
})
export class PlatformAdminComponent implements OnInit {
  plans: any[] = [];
  templates: any[] = [];

  constructor(private platform: PlatformService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.platform.getPlans().subscribe(data => this.plans = data);
    this.platform.getTemplates().subscribe(data => this.templates = data);
  }
}
