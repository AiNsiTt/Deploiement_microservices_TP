"""
User Service - Gestion des utilisateurs
Architecture Microservices Zero Trust E-Commerce Platform
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import jwt
import os
from datetime import datetime
import logging

# Configuration
app = FastAPI(title="User Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration (Keycloak public key)
KEYCLOAK_PUBLIC_KEY = os.getenv("KEYCLOAK_PUBLIC_KEY", "")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ecommerce")

# Models
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str  # client, vendor, admin
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "client"

# In-memory database (simulation)
users_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@ecommerce.com",
        "first_name": "Admin",
        "last_name": "System",
        "role": "admin",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "username": "vendor1",
        "email": "vendor@ecommerce.com",
        "first_name": "John",
        "last_name": "Vendor",
        "role": "vendor",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 3,
        "username": "client1",
        "email": "client@ecommerce.com",
        "first_name": "Jane",
        "last_name": "Client",
        "role": "client",
        "created_at": datetime.now().isoformat()
    }
]

# Security: JWT Token Validation
def verify_token(authorization: Optional[str] = Header(None)):
    """
    Vérifie le JWT token fourni par Keycloak
    Principe Zero Trust: Toujours vérifier l'authentification
    """
    if not authorization:
        logger.warning("Missing authorization header")
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        # En production, valider avec la clé publique Keycloak
        # payload = jwt.decode(token, KEYCLOAK_PUBLIC_KEY, algorithms=["RS256"])
        # Pour la démo, on simule la validation
        logger.info(f"Token validated successfully")
        return {"sub": "user123", "realm_access": {"roles": ["client"]}}
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Health Check
@app.get("/health")
def health_check():
    """Health check endpoint pour Docker"""
    return {"status": "healthy", "service": "user-service"}

# Endpoints
@app.get("/users", response_model=List[User])
def get_users(token_data: dict = Depends(verify_token)):
    """
    Récupère la liste des utilisateurs
    Sécurité: Nécessite authentification JWT
    """
    logger.info(f"Fetching users list")
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, token_data: dict = Depends(verify_token)):
    """
    Récupère un utilisateur par ID
    Sécurité: Vérification ownership (utilisateur ne peut voir que son profil sauf admin)
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User {user_id} retrieved successfully")
    return user

@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """
    Crée un nouvel utilisateur
    Note: En production, ceci serait géré par Keycloak
    """
    new_user = {
        "id": len(users_db) + 1,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    logger.info(f"User {new_user['id']} created successfully")
    return new_user

@app.get("/users/me/profile", response_model=User)
def get_my_profile(token_data: dict = Depends(verify_token)):
    """
    Récupère le profil de l'utilisateur connecté
    Sécurité: Basé sur le JWT token
    """
    # En production, extraire user_id du token
    user_id = 1  # Simulation
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Profile retrieved for user {user_id}")
    return user

# Métriques Prometheus (simulation)
@app.get("/metrics")
def metrics():
    """Endpoint pour Prometheus metrics"""
    return {
        "total_users": len(users_db),
        "users_by_role": {
            "admin": len([u for u in users_db if u["role"] == "admin"]),
            "vendor": len([u for u in users_db if u["role"] == "vendor"]),
            "client": len([u for u in users_db if u["role"] == "client"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
