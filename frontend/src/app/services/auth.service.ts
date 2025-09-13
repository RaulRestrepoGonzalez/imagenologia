import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  id: string;
  email: string;
  nombre: string;
  apellidos?: string;
  role: 'admin' | 'radiologo' | 'secretario' | 'paciente';
  is_active: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
  paciente_id?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  apellidos?: string;
  role: 'admin' | 'radiologo' | 'secretario' | 'paciente';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = `${environment.apiUrl}/api`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(null);

  public currentUser$ = this.currentUserSubject.asObservable();
  public token$ = this.tokenSubject.asObservable();

  constructor(private http: HttpClient) {
    // Load user and token from localStorage on service initialization
    this.loadStoredAuth();
  }

  private loadStoredAuth(): void {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.tokenSubject.next(token);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        this.clearStoredAuth();
      }
    }
  }

  private storeAuth(token: string, user: User): void {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('current_user', JSON.stringify(user));
    this.tokenSubject.next(token);
    this.currentUserSubject.next(user);
  }

  private clearStoredAuth(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/login`, credentials)
      .pipe(
        tap(response => {
          this.storeAuth(response.access_token, response.user);
        })
      );
  }

  register(userData: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.API_URL}/auth/register`, userData);
  }

  registerPatient(userData: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/auth/register-patient`, userData)
      .pipe(
        tap(response => {
          this.storeAuth(response.access_token, response.user);
        })
      );
  }

  logout(): void {
    this.clearStoredAuth();
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/auth/me`);
  }

  refreshUserData(): Observable<User> {
    return this.getCurrentUser().pipe(
      tap(user => {
        const currentToken = this.tokenSubject.value;
        if (currentToken) {
          this.storeAuth(currentToken, user);
        }
      })
    );
  }

  isAuthenticated(): boolean {
    return this.tokenSubject.value !== null && this.currentUserSubject.value !== null;
  }

  getToken(): string | null {
    return this.tokenSubject.value;
  }

  getUser(): User | null {
    return this.currentUserSubject.value;
  }

  hasRole(roles: string[]): boolean {
    const user = this.getUser();
    return user ? roles.includes(user.role) : false;
  }

  isAdmin(): boolean {
    return this.hasRole(['admin']);
  }

  isStaff(): boolean {
    return this.hasRole(['admin', 'radiologo', 'secretario']);
  }

  isMedicalStaff(): boolean {
    return this.hasRole(['admin', 'radiologo']);
  }

  isPatient(): boolean {
    return this.hasRole(['paciente']);
  }

  getAuthHeaders(): { [key: string]: string } {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}
