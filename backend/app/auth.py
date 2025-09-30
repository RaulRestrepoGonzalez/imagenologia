"""
Authentication utilities and JWT handling
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract user data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "email": email,
            "user_id": user_id,
            "role": role
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(allowed_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: dict = Depends(verify_token)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return current_user
    return role_checker

# Role-based access control helpers
def require_admin(current_user: dict = Depends(verify_token)):
    """Require admin role"""
    return require_role(["admin"])(current_user)

def require_staff(current_user: dict = Depends(verify_token)):
    """Require staff roles (admin, radiologo, secretario)"""
    return require_role(["admin", "radiologo", "secretario"])(current_user)

def require_medical_staff(current_user: dict = Depends(verify_token)):
    """Require medical staff (admin, radiologo)"""
    return require_role(["admin", "radiologo"])(current_user)

# Import here to avoid circular imports
from .schemas import User, UserRole
from .database import db

async def get_current_user(token_data: dict = Depends(verify_token)) -> User:
    """Get current user from token"""
    from bson import ObjectId
    
    # Buscar por _id (ObjectId de MongoDB)
    user_data = await db.users.find_one({"_id": ObjectId(token_data["user_id"])})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    # Agregar campo 'id' si no existe (para compatibilidad con Pydantic)
    if "id" not in user_data:
        user_data["id"] = str(user_data["_id"])
    
    user = User(**user_data)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user

def get_current_active_user(allowed_roles: list[UserRole] = None):
    """Factory function to create a dependency that checks user roles"""
    async def check_user(current_user: User = Depends(get_current_user)) -> User:
        # Check role if specified
        if allowed_roles and current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return current_user
    return check_user
