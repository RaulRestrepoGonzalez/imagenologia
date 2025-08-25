Este backend implementa una API REST para gestionar pacientes, órdenes, citas, notificaciones y DICOM.

## Stack Tecnológico
- Python 3.13.3
- FastAPI
- MongoDB (motor)
- JWT Auth
- Email notifications
- DICOM Metadata Handling

## Estructura del Proyecto
Ver carpetas `app/models`, `app/routers`, `app/services`, `app/utils`.

## Cómo correr el proyecto y pasos para ejecutar de forma segura
```bash
1. Crear un archivo `.env` en la raíz del proyecto y agregar las variables de entorno necesarias con el comando `python -m venv .venv`
2. ACtivar con el comnado `source .venv/bin/activate.fish` o `source env/bin/activate`
3. Actualizar librerias con el comando `pip install --upgrade pip setuptools wheel`
4. Instalar las dependencias con el comando `pip install -r requirements.txt`
```

## Variables de Entorno
- `MONGODB_URI`
- `SECRET_KEY`
- `MAIL_SENDER`

---
© Proyecto de grado 2025 - Universidad Popular del Cesar
