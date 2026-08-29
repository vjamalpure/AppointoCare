import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }

    // Role-based access
    const expectedRole = route.data['expectedRole']; // 'Admin' or 'Organization'
    const userRole = this.authService.getUserRole();

    if (expectedRole && expectedRole !== userRole) {
      // Role mismatch → redirect to login or dashboard
      this.router.navigate(['/login']);
      return false;
    }

    return true;
  }
}
