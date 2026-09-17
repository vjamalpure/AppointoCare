import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, tap } from 'rxjs';
import { jwtDecode } from 'jwt-decode';
import { Router } from '@angular/router';

export interface DecodedToken {
  identity?: string;
  role?: string;
  username?: string;
  organization_name?: string;
  organization_id?: string;
  exp?: number;
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private readonly TOKEN_KEY = 'appointocare_access_token';
  private readonly REFRESH_KEY = 'appointocare_refresh_token';
  private readonly ROLE_KEY = 'appointocare_user_role';
  private readonly ORG_NAME_KEY = 'OrgName';

  constructor(private http: HttpClient, private router: Router) {}

  login(username: string, password: string, code?: string, rememberMe = false): Observable<any> {
    const payload: any = { username, password };
    if (code) {
      payload.code = code;
    }
    return this.http.post<any>(`${this.apiUrl}/auth/login`, payload).pipe(
      tap(res => {
        if (res?.access_token) {
          const storage = rememberMe ? localStorage : sessionStorage;
          storage.setItem(this.TOKEN_KEY, res.access_token);
          if (res.refresh_token) {
            storage.setItem(this.REFRESH_KEY, res.refresh_token);
          }
          if (res.role) {
            storage.setItem(this.ROLE_KEY, res.role);
          }
          if (res.organization_name) {
            storage.setItem(this.ORG_NAME_KEY, res.organization_name);
          }
        }
      })
    );
  }

  saveOrgName(name: string, rememberMe = false): void {
    if (!name) return;
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(this.ORG_NAME_KEY, name);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.ROLE_KEY);
    localStorage.removeItem(this.ORG_NAME_KEY);
    sessionStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_KEY);
    sessionStorage.removeItem(this.ROLE_KEY);
    sessionStorage.removeItem(this.ORG_NAME_KEY);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;
    try {
      const decoded = jwtDecode<DecodedToken>(token);
      if (decoded.exp && decoded.exp * 1000 < Date.now()) {
        return false;
      }
      return true;
    } catch {
      return false;
    }
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY) || sessionStorage.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY) || sessionStorage.getItem(this.REFRESH_KEY);
  }

  getDecodedToken(): DecodedToken | null {
    const token = this.getAccessToken();
    if (!token) return null;
    try {
      return jwtDecode<DecodedToken>(token);
    } catch {
      return null;
    }
  }

  getUserRole(): string {
    const decoded = this.getDecodedToken();
    if (decoded?.role) return decoded.role;
    return localStorage.getItem(this.ROLE_KEY) || sessionStorage.getItem(this.ROLE_KEY) || '';
  }

  getUsername(): string {
    const decoded = this.getDecodedToken();
    return decoded?.username || '';
  }

  getOrganizationId(): string | null {
    const decoded = this.getDecodedToken();
    return decoded?.organization_id || null;
  }

  getOrganizationName(): string | null {
    const decoded = this.getDecodedToken();
    return decoded?.organization_name || localStorage.getItem(this.ORG_NAME_KEY) || sessionStorage.getItem(this.ORG_NAME_KEY) || null;
  }

  forgotPassword(payload: { username: string; role: string; code?: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/forgot-password`, payload);
  }

  resetPassword(payload: { token: string; new_password: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/reset-password`, payload);
  }
}
