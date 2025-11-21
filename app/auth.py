from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from .queries.q_auth import add_admin, get_login


# Definisikan model Pydantic untuk validasi input
class AdminCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    
# Pydantic model untuk login
class LoginRequest(BaseModel):
    email: str
    password: str

# Pydantic model untuk response login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_user: int
    name: str
    email: str
    role: str

router = APIRouter()

# @router.post("/auth/add-admin", tags=["Auth"])
# async def create_admin(admin_request: AdminCreateRequest):
#     """Endpoint untuk menambah admin baru"""
#     # Ambil data dari request body
#     admin = add_admin(admin_request.username, admin_request.email, admin_request.password)
    
#     if not admin:
#         raise HTTPException(status_code=400, detail="Failed to create admin")
    
#     return {"message": "Admin created successfully", "admin": admin}


# Endpoint untuk login
@router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(login_request: LoginRequest):
    """Login menggunakan email + password"""
    # Ambil data dari request body
    payload = login_request.dict()

    # Validasi input
    if not payload.get('email') or not payload.get('password'):
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        jwt_response = get_login(payload)
        if jwt_response is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "access_token": jwt_response['access_token'],
            "token_type": "bearer",
            "id_user": jwt_response['id_user'],
            "name": jwt_response['name'],
            "email": jwt_response['email'],
            "role": jwt_response['role'],
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")