import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = os.getenv("SMTP_PORT", "587")
        self.smtp_port = int(smtp_port) if smtp_port else 587
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_name = os.getenv("FROM_NAME", "Centro de Imagenología")
        
        # Verificar configuración
        if not self.smtp_username or not self.smtp_password:
            logging.warning("Configuración SMTP incompleta. Los emails no se enviarán.")
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Enviar email general"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logging.error("Configuración SMTP incompleta")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.smtp_username}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar versión de texto plano
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Agregar versión HTML si se proporciona
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logging.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Error enviando email a {to_email}: {str(e)}")
            return False

    async def send_appointment_reminder(self, paciente_email: str, paciente_nombre: str, 
                                      fecha_cita: str, tipo_estudio: str) -> bool:
        """Enviar recordatorio de cita"""
        subject = f"Recordatorio de cita para {tipo_estudio}"
        
        body = f"""
        Estimado/a {paciente_nombre},
        
        Le recordamos que tiene programada una cita para {tipo_estudio} 
        el día {fecha_cita}.
        
        Por favor, presentarse 15 minutos antes de la hora programada.
        
        Saludos cordiales,
        {self.from_name}
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Recordatorio de Cita</h2>
            <p>Estimado/a <strong>{paciente_nombre}</strong>,</p>
            <p>Le recordamos que tiene programada una cita para <strong>{tipo_estudio}</strong> 
            el día <strong>{fecha_cita}</strong>.</p>
            <p>Por favor, presentarse 15 minutos antes de la hora programada.</p>
            <br>
            <p>Saludos cordiales,<br>
            <strong>{self.from_name}</strong></p>
        </body>
        </html>
        """
        
        return await self.send_email(paciente_email, subject, body, html_body)

    async def send_study_results(self, paciente_email: str, paciente_nombre: str, 
                               tipo_estudio: str, fecha_estudio: str) -> bool:
        """Enviar notificación de resultados de estudio"""
        subject = f"Resultados disponibles - {tipo_estudio}"
        
        body = f"""
        Estimado/a {paciente_nombre},
        
        Los resultados de su estudio de {tipo_estudio} realizado el {fecha_estudio} 
        están disponibles en su portal de paciente.
        
        Por favor, inicie sesión para consultarlos.
        
        Saludos cordiales,
        {self.from_name}
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Resultados Disponibles</h2>
            <p>Estimado/a <strong>{paciente_nombre}</strong>,</p>
            <p>Los resultados de su estudio de <strong>{tipo_estudio}</strong> 
            realizado el <strong>{fecha_estudio}</strong> están disponibles 
            en su portal de paciente.</p>
            <p>Por favor, inicie sesión para consultarlos.</p>
            <br>
            <p>Saludos cordiales,<br>
            <strong>{self.from_name}</strong></p>
        </body>
        </html>
        """
        
        return await self.send_email(paciente_email, subject, body, html_body)

    async def send_welcome_message(self, paciente_email: str, paciente_nombre: str) -> bool:
        """Enviar mensaje de bienvenida"""
        subject = "Bienvenido a nuestro centro médico"
        
        body = f"""
        Estimado/a {paciente_nombre},
        
        Le damos la bienvenida a {self.from_name}.
        
        Su cuenta ha sido creada exitosamente y puede acceder a su portal 
        de paciente para gestionar sus citas y consultar resultados.
        
        Saludos cordiales,
        {self.from_name}
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>¡Bienvenido!</h2>
            <p>Estimado/a <strong>{paciente_nombre}</strong>,</p>
            <p>Le damos la bienvenida a <strong>{self.from_name}</strong>.</p>
            <p>Su cuenta ha sido creada exitosamente y puede acceder a su portal 
            de paciente para gestionar sus citas y consultar resultados.</p>
            <br>
            <p>Saludos cordiales,<br>
            <strong>{self.from_name}</strong></p>
        </body>
        </html>
        """
        
        return await self.send_email(paciente_email, subject, body, html_body)

    async def send_password_reset(self, paciente_email: str, reset_token: str) -> bool:
        """Enviar enlace para restablecer contraseña"""
        subject = "Restablecimiento de contraseña"
        
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={reset_token}"
        
        body = f"""
        Ha solicitado restablecer su contraseña.
        
        Para continuar, haga clic en el siguiente enlace:
        {reset_url}
        
        Este enlace expirará en 1 hora.
        
        Si no solicitó este cambio, ignore este mensaje.
        
        Saludos cordiales,
        {self.from_name}
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Restablecimiento de Contraseña</h2>
            <p>Ha solicitado restablecer su contraseña.</p>
            <p>Para continuar, haga clic en el siguiente enlace:</p>
            <p><a href="{reset_url}">Restablecer Contraseña</a></p>
            <p>Este enlace expirará en 1 hora.</p>
            <p>Si no solicitó este cambio, ignore este mensaje.</p>
            <br>
            <p>Saludos cordiales,<br>
            <strong>{self.from_name}</strong></p>
        </body>
        </html>
        """
        
        return await self.send_email(paciente_email, subject, body, html_body)

    def test_connection(self) -> bool:
        """Probar conexión SMTP"""
        try:
            if not self.smtp_username or not self.smtp_password:
                return False
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                return True
                
        except Exception as e:
            logging.error(f"Error probando conexión SMTP: {str(e)}")
            return False
    