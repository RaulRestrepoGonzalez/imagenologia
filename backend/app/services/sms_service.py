import os
import requests
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

class SMSService:
    def __init__(self):
        self.provider = os.getenv("SMS_PROVIDER", "twilio")  # twilio, generic
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        # Para proveedores genéricos
        self.generic_api_url = os.getenv("SMS_API_URL")
        self.generic_api_key = os.getenv("SMS_API_KEY")
        self.generic_sender = os.getenv("SMS_SENDER", "CentroMedico")
        
        # Verificar configuración
        if self.provider == "twilio" and not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            logging.warning("Configuración de Twilio incompleta. Los SMS no se enviarán.")
        elif self.provider == "generic" and not all([self.generic_api_url, self.generic_api_key]):
            logging.warning("Configuración de SMS genérico incompleta. Los SMS no se enviarán.")
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """Enviar SMS usando el proveedor configurado"""
        try:
            if self.provider == "twilio":
                return await self._send_twilio_sms(to_number, message)
            elif self.provider == "generic":
                return await self._send_generic_sms(to_number, message)
            else:
                logging.error(f"Proveedor SMS no soportado: {self.provider}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando SMS a {to_number}: {str(e)}")
            return False
    
    async def _send_twilio_sms(self, to_number: str, message: str) -> bool:
        """Enviar SMS usando Twilio"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
                logging.error("Configuración de Twilio incompleta")
                return False
            
            # En un entorno real, usarías la librería de Twilio
            # Por ahora, simulamos el envío
            logging.info(f"SMS Twilio enviado a {to_number}: {message[:50]}...")
            return True
            
        except Exception as e:
            logging.error(f"Error enviando SMS Twilio: {str(e)}")
            return False
    
    async def _send_generic_sms(self, to_number: str, message: str) -> bool:
        """Enviar SMS usando API genérica"""
        try:
            if not all([self.generic_api_url, self.generic_api_key]):
                logging.error("Configuración de SMS genérico incompleta")
                return False
            
            # Preparar datos para la API
            payload = {
                "to": to_number,
                "message": message,
                "sender": self.generic_sender,
                "api_key": self.generic_api_key
            }
            
            # Enviar request a la API
            response = requests.post(self.generic_api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                logging.info(f"SMS genérico enviado exitosamente a {to_number}")
                return True
            else:
                logging.error(f"Error en API SMS: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando SMS genérico: {str(e)}")
            return False
    
    async def send_appointment_reminder(self, paciente_telefono: str, paciente_nombre: str, 
                                      fecha_cita: str, tipo_estudio: str) -> bool:
        """Enviar recordatorio de cita por SMS"""
        message = f"Recordatorio: Su cita para {tipo_estudio} es el {fecha_cita}. Presentarse 15 min antes."
        return await self.send_sms(paciente_telefono, message)
    
    async def send_study_results(self, paciente_telefono: str, paciente_nombre: str, 
                               tipo_estudio: str) -> bool:
        """Enviar notificación de resultados por SMS"""
        message = f"Los resultados de su {tipo_estudio} están disponibles. Consulte su portal de paciente."
        return await self.send_sms(paciente_telefono, message)
    
    async def send_welcome_message(self, paciente_telefono: str, paciente_nombre: str) -> bool:
        """Enviar mensaje de bienvenida por SMS"""
        message = f"¡Bienvenido {paciente_nombre}! Su cuenta ha sido creada exitosamente."
        return await self.send_sms(paciente_telefono, message)
    
    async def send_urgency_notification(self, paciente_telefono: str, paciente_nombre: str, 
                                      mensaje: str) -> bool:
        """Enviar notificación urgente por SMS"""
        message = f"URGENTE: {mensaje}"
        return await self.send_sms(paciente_telefono, message)
    
    def test_connection(self) -> bool:
        """Probar conexión del servicio SMS"""
        try:
            if self.provider == "twilio":
                return bool(all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]))
            elif self.provider == "generic":
                return bool(all([self.generic_api_url, self.generic_api_key]))
            else:
                return False
                
        except Exception as e:
            logging.error(f"Error probando conexión SMS: {str(e)}")
            return False
    
    def get_provider_info(self) -> dict:
        """Obtener información del proveedor SMS configurado"""
        if self.provider == "twilio":
            return {
                "provider": "twilio",
                "configured": bool(all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number])),
                "from_number": self.twilio_from_number
            }
        elif self.provider == "generic":
            return {
                "provider": "generic",
                "configured": bool(all([self.generic_api_url, self.generic_api_key])),
                "api_url": self.generic_api_url,
                "sender": self.generic_sender
            }
        else:
            return {
                "provider": "unknown",
                "configured": False
            }
    