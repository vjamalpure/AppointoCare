import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { tap, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { jwtDecode } from 'jwt-decode';
import { Observable, throwError } from 'rxjs';

interface LoginResp {
  access_token: string;
  refresh_token?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private accessTokenKey = 'appointocare_token';
  private refreshTokenKey = 'appointocare_refresh_token';

  constructor(private http: HttpClient, private router: Router) {}

  // Login API aligned with Flask backend
  login(username: string, password: string, code?: string, rememberMe: boolean = true) {
    return this.http.post<LoginResp>(`${environment.apiUrl}/auth/login`, {
      username,
      password,
      code
    }).pipe(
      tap(resp => {
        if (resp?.access_token) {
          this.saveTokens(resp.access_token, resp.refresh_token || '', rememberMe);
        }
      })
    );
  }

  logout() {
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    sessionStorage.removeItem(this.accessTokenKey);
    sessionStorage.removeItem(this.refreshTokenKey);
    this.router.navigate(['/login']);
  }

  // Get token from storage
  getToken(): string | null {
    return localStorage.getItem(this.accessTokenKey) || sessionStorage.getItem(this.accessTokenKey);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey) || sessionStorage.getItem(this.refreshTokenKey);
  }
  // Check login & token expiration
  isLoggedIn(): boolean {
    const token = this.getToken();
    if (!token) return false;

    const decoded: any = this.getDecodedToken();
    if (!decoded) return false;

    const exp = decoded.exp;
    if (!exp) return true; // no exp field
    const now = Math.floor(Date.now() / 1000);
    return exp > now;
  }

  getDecodedToken(): any {
    const token = this.getToken();
    if (!token) return null;
    try { return (jwtDecode as any)(token); } catch { return null; }
  }

  getUserRole(): string | null {
    return this.getDecodedToken()?.role ?? null;
  }

  getOrganizationId(): number | null {
    return this.getDecodedToken()?.organization_id ?? null;
  }

  getOrganizationName(): string | null {
    return this.getDecodedToken()?.organization_name ?? null;
  }

  saveTokens(accessToken: string, refreshToken: string, rememberMe: boolean = true) {
    if (rememberMe) {
      localStorage.setItem(this.accessTokenKey, accessToken);
      if (refreshToken) {
        localStorage.setItem(this.refreshTokenKey, refreshToken);
      }
    } else {
      sessionStorage.setItem(this.accessTokenKey, accessToken);
      if (refreshToken) {
        sessionStorage.setItem(this.refreshTokenKey, refreshToken);
      }
    }
  }

  saveAccessToken(token: string, rememberMe: boolean = true) {
    if (rememberMe) {
      localStorage.setItem(this.accessTokenKey, token);
    } else {
      sessionStorage.setItem(this.accessTokenKey, token);
    }
  }

  refreshToken(): Observable<{ access_token: string }> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post<{ access_token: string }>(`${environment.apiUrl}/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      tap(resp => {
        if (resp?.access_token) {
          const rememberMe = !!localStorage.getItem(this.refreshTokenKey);
          this.saveAccessToken(resp.access_token, rememberMe);
        }
      }),
      catchError(err => throwError(() => err))
    );
  }

  forgotPassword(username: string, role: string, code?: string) {
    return this.http.post(`${environment.apiUrl}/auth/forgot-password`, { username, role, code });
  }

  resetPassword(token: string, newPassword: string) {
    return this.http.post(`${environment.apiUrl}/auth/reset-password`, { token, new_password: newPassword });
  }

  saveOrgName(OrgName: string, rememberMe: boolean = true) {
    if (rememberMe) {
      localStorage.setItem('OrgName', OrgName);
    } else {
      sessionStorage.setItem('OrgName', OrgName);
    }
  }
}