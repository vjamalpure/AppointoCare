import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
      return false;
    }

    const expectedRole = route.data['expectedRole'];
    if (!expectedRole) {
      return true;
    }

    const userRole = this.authService.getUserRole();
    const isOrgLevel = ['Organization', 'Manager', 'Staff', 'Doctor', 'Therapist', 'Stylist', 'Advisor', 'Underwriter', 'Broker', 'Consultant', 'Specialist'].includes(userRole);
    const isAdminLevel = userRole === 'Admin' || userRole === 'SuperAdmin';

    if (Array.isArray(expectedRole)) {
      if (expectedRole.includes(userRole)) {
        return true;
      }
      if (expectedRole.includes('Staff') && isOrgLevel) {
        return true;
      }
      if (expectedRole.includes('Admin') && isAdminLevel) {
        return true;
      }
    } else {
      if (expectedRole === userRole) {
        return true;
      }
      if (expectedRole === 'Admin' && isAdminLevel) {
        return true;
      }
      if ((expectedRole === 'Staff' || expectedRole === 'Organization') && isOrgLevel) {
        return true;
      }
    }

    // Role mismatch -> redirect to appropriate home
    if (isAdminLevel) {
      this.router.navigate(['/admin-dashboard']);
    } else {
      this.router.navigate(['/org-dashboard']);
    }
    return false;
  }
}
