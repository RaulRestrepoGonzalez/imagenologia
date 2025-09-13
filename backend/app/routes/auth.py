"""
Authentication routes for login, register, and user management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import UserCreate, UserLogin, User, Token, UserRole
from app.database import get_database
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    verify_token,
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import datetime, timedelta
from bson import ObjectId
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario con este email ya existe"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user_dict = {
        "email": user_data.email,
        "nombre": user_data.nombre,
        "apellidos": user_data.apellidos,
        "role": user_data.role,
        "is_active": user_data.is_active,
        "password_hash": hashed_password,
        "paciente_id": user_data.paciente_id,
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now()
    }
    
    # Insert user
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string and remove password hash
    new_user["id"] = str(new_user["_id"])
    del new_user["_id"]
    del new_user["password_hash"]
    
    logger.info(f"Usuario registrado: {user_data.email} con rol {user_data.role}")
    return User(**new_user)

@router.post("/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["email"],
            "user_id": str(user["_id"]),
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    # Prepare user data for response
    user_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "nombre": user["nombre"],
        "apellidos": user.get("apellidos"),
        "role": user["role"],
        "is_active": user["is_active"],
        "fecha_creacion": user["fecha_creacion"],
        "fecha_actualizacion": user["fecha_actualizacion"],
        "paciente_id": user.get("paciente_id")
    }
    
    logger.info(f"Usuario autenticado: {login_data.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=User(**user_data)
    )

@router.get("/auth/me", response_model=User)
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current authenticated user information"""
    db = get_database()
    
    user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    user_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "nombre": user["nombre"],
        "apellidos": user.get("apellidos"),
        "role": user["role"],
        "is_active": user["is_active"],
        "fecha_creacion": user["fecha_creacion"],
        "fecha_actualizacion": user["fecha_actualizacion"],
        "paciente_id": user.get("paciente_id")
    }
    
    return User(**user_data)

@router.post("/auth/register-patient", response_model=Token)
async def register_patient_with_user(user_data: UserCreate):
    """Register a patient and create associated user account"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario con este email ya existe"
        )
    
    # Force role to be patient
    user_data.role = UserRole.PACIENTE
    
    # Create patient record first if paciente_id is not provided
    if not user_data.paciente_id:
        # Create basic patient record
        patient_data = {
            "nombre": user_data.nombre,
            "apellidos": user_data.apellidos,
            "email": user_data.email,
            "identificacion": "",  # Will need to be filled later
            "tipo_identificacion": "CC",
            "telefono": "",
            "fecha_nacimiento": datetime.now(),
            "direccion": "",
            "genero": "",
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": datetime.now()
        }
        
        patient_result = await db.pacientes.insert_one(patient_data)
        user_data.paciente_id = str(patient_result.inserted_id)
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user_dict = {
        "email": user_data.email,
        "nombre": user_data.nombre,
        "apellidos": user_data.apellidos,
        "role": user_data.role,
        "is_active": user_data.is_active,
        "password_hash": hashed_password,
        "paciente_id": user_data.paciente_id,
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now()
    }
    
    # Insert user
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": new_user["email"],
            "user_id": str(new_user["_id"]),
            "role": new_user["role"]
        },
        expires_delta=access_token_expires
    )
    
    # Prepare user data for response
    user_response_data = {
        "id": str(new_user["_id"]),
        "email": new_user["email"],
        "nombre": new_user["nombre"],
        "apellidos": new_user.get("apellidos"),
        "role": new_user["role"],
        "is_active": new_user["is_active"],
        "fecha_creacion": new_user["fecha_creacion"],
        "fecha_actualizacion": new_user["fecha_actualizacion"],
        "paciente_id": new_user.get("paciente_id")
    }
    
    logger.info(f"Paciente registrado: {user_data.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=User(**user_response_data)
    )

@router.get("/auth/users", response_model=list[User])
async def get_all_users(current_user: dict = Depends(require_admin)):
    """Get all users (admin only)"""
    db = get_database()
    
    users = []
    async for user in db.users.find():
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "nombre": user["nombre"],
            "apellidos": user.get("apellidos"),
            "role": user["role"],
            "is_active": user["is_active"],
            "fecha_creacion": user["fecha_creacion"],
            "fecha_actualizacion": user["fecha_actualizacion"],
            "paciente_id": user.get("paciente_id")
        }
        users.append(User(**user_data))
    
    return users
