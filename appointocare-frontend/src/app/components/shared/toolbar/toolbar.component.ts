import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent implements OnInit {
  @Input() username: string = '';
  @Input() organizationName: string = '';
  @Input() userRole: string = '';
  @Output() toggleSidebar = new EventEmitter<void>();

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    if (!this.username || !this.userRole) {
      const decoded = this.authService.getDecodedToken();
      if (decoded) {
        this.username = this.username || decoded.username || 'User';
        this.userRole = this.userRole || decoded.role || '';
        this.organizationName = this.organizationName || decoded.organization_name || localStorage.getItem('OrgName') || '';
      }
    }
  }

  logout(): void {
    this.authService.logout();
  }
}
