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

## Cómo correr el proyecto
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Variables de Entorno
- `MONGODB_URI`
- `SECRET_KEY`
- `MAIL_SENDER`

---

© Proyecto de grado 2025 - Universidad Popular del Cesar
