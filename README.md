# 📦 Sistema de Gestión Integral para Imagenología

Este repositorio contiene el código fuente del sistema de gestión integral para automatización del servicio de imágenes diagnósticas, desarrollado como proyecto de grado para la **IPS Centro de Imagenología Cástulo Ropain Lobo S.A.S.**

## 🧩 Tecnologías Utilizadas

| Componente   | Tecnología            |
|--------------|------------------------|
| Backend      | Python 3.13.3 + FastAPI |
| Base de Datos| MongoDB (NoSQL)        |
| Frontend     | Angular 19.2.10        |
| Infraestructura | AWS EC2 + S3 + DocumentDB |

## 📁 Estructura del Repositorio

```
/backend
/Docker
/frontend
```

## 🚀 Cómo Ejecutar el Proyecto (Backend)

### 1. Clonar el repositorio
```bash
git clone git@github.com:RaulRestrepoGonzalez/imagenologia.git
cd proyecto-imagenologia/backend
```

### 2. Crear y activar entorno virtual (opcional pero recomendado)
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear archivo `.env`
```ini
MONGODB_URI=mongodb://localhost:27017
SECRET_KEY=supersecretkey
MAIL_SENDER=notificaciones@ips.com
```

### 5. Ejecutar el servidor
```bash
uvicorn app.main:app --reload
```

### 6. Probar en navegador o Postman:
```
http://localhost:8000/docs
```

---

## 📘 Manual de Usuario (Resumen)

### 🔐 Autenticación
- **POST** `/auth/token`: Iniciar sesión (usuario y contraseña).

### 👨‍⚕️ Módulo de Pacientes
- **GET** `/patients/`: Listar pacientes.
- **POST** `/patients/`: Crear paciente.
- **PUT/DELETE** `/patients/{id}`: Modificar o eliminar paciente.

### 📄 Módulo de Órdenes
- **POST** `/orders/`: Crear orden.
- **GET** `/orders/`: Listar órdenes.

### 📅 Módulo de Citas
- **POST** `/appointments/`: Crear cita.
- **GET** `/appointments/`: Listar citas.

### 📢 Notificaciones
- **POST** `/notifications/send`: Enviar correo (simulado en consola).

---

## 📦 Funcionalidades Clave

- 📌 Gestión integral de pacientes, órdenes y citas.
- 📧 Notificaciones automáticas vía correo (configurable).
- 🧠 Extracción de metadatos de imágenes médicas DICOM.
- 🔐 Seguridad con JWT y roles.

---

## 👥 Autores
- Raúl Alfonso Restrepo González  
- Ricardo Javier Mejía Ruiz

© Proyecto de grado 2025 - Universidad Popular del Cesar

---

## 📄 Licencia
Este proyecto está licenciado bajo MIT. Libre para uso académico y educativo.

