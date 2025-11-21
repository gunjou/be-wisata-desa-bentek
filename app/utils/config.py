import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader


# Secret key dan algoritma untuk JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12  # Token kadaluarsa dalam 12 jam

# Load .env yang akan digunakan
load_dotenv()

# APIKeyHeader digunakan untuk mengambil token JWT dari header Authorization
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


# === Konfigurasi Database === #
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

DATABASE_URL = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}'

# ⛽️ Engine dibuat sekali dan dipakai ulang (pool aman)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True  # opsional tapi direkomendasikan
)

def get_connection():
    return engine

# Fungsi untuk membuat JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fungsi untuk validasi token JWT
def validate_jwt_token(authorization: str = Depends(api_key_header)):
    if authorization is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")  # Menghapus "Bearer" agar hanya menyisakan token
    return token