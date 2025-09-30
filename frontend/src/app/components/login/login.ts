import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatTabsModule } from '@angular/material/tabs';
import { AuthService, LoginRequest, RegisterRequest } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatSnackBarModule,
    MatSelectModule,
    MatTabsModule,
  ],
  templateUrl: './login.html',
  styleUrls: ['./login.scss'],
})
export class LoginComponent {
  loginForm: FormGroup;
  registerForm: FormGroup;
  isLoading: boolean = false;
  hidePassword: boolean = true;
  hideConfirmPassword: boolean = true;
  returnUrl: string = '/';

  roles = [
    { value: 'admin', label: 'Administrador' },
    { value: 'radiologo', label: 'Radiólogo' },
    { value: 'secretario', label: 'Secretario' },
    { value: 'tecnico', label: 'Técnico' },
    { value: 'paciente', label: 'Paciente' }
  ];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
    private authService: AuthService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });

    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]],
      nombre: ['', [Validators.required]],
      apellidos: [''],
      role: ['paciente', [Validators.required]]
    }, { validators: this.passwordMatchValidator });

    // Get return URL from route parameters or default to '/'
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    
    if (confirmPassword?.hasError('passwordMismatch')) {
      confirmPassword.setErrors(null);
    }
    
    return null;
  }

  onLogin(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      const loginData: LoginRequest = this.loginForm.value;

      this.authService.login(loginData).subscribe({
        next: (response) => {
          this.showMessage('¡Inicio de sesión exitoso!', 'success');
          this.router.navigate([this.returnUrl]);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Login error:', error);
          this.showMessage(error.error?.detail || 'Error al iniciar sesión', 'error');
          this.isLoading = false;
        }
      });
    }
  }

  onRegister(): void {
    if (this.registerForm.valid) {
      this.isLoading = true;
      const registerData: RegisterRequest = {
        email: this.registerForm.value.email,
        password: this.registerForm.value.password,
        nombre: this.registerForm.value.nombre,
        apellidos: this.registerForm.value.apellidos,
        role: this.registerForm.value.role
      };

      // Use different endpoint for patient registration
      if (registerData.role === 'paciente') {
        this.authService.registerPatient(registerData).subscribe({
          next: (response: any) => {
            this.showMessage('¡Registro exitoso!', 'success');
            this.router.navigate([this.returnUrl]);
            this.isLoading = false;
          },
          error: (error: any) => {
            console.error('Register error:', error);
            this.showMessage(error.error?.detail || 'Error al registrarse', 'error');
            this.isLoading = false;
          }
        });
      } else {
        this.authService.register(registerData).subscribe({
          next: (response: any) => {
            this.showMessage('Cuenta creada. Contacte al administrador para activación.', 'success');
            this.isLoading = false;
          },
          error: (error: any) => {
            console.error('Register error:', error);
            this.showMessage(error.error?.detail || 'Error al registrarse', 'error');
            this.isLoading = false;
          }
        });
      }
    }
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
    });
  }

  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword = !this.hideConfirmPassword;
  }
}
