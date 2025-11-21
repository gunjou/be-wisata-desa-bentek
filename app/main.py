from fastapi import FastAPI

from .auth import router as auth_router
from .destinasi import router as destinasi_router
from .paket import router as paket_router
from .blog import router as blog_router


# Metadata untuk tags
tags_metadata = [
    {"name": "Auth", "description": "Endpoint untuk autentikasi pengguna (login, logout, dll)."},
    {"name": "Destinasi", "description": "Endpoint untuk manajemen destinasi wisata."},
    {"name": "Paket", "description": "Endpoint untuk manajemen paket wisata."},
    {"name": "Blog", "description": "Endpoint untuk mengelola blog informasi."},
]

# Inisialisasi FastAPI dengan tags metadata
app = FastAPI(
    title="Desa Wisata API",
    description="API untuk mengelola destinasi wisata dan paket wisata.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"docExpansion": "none"},
)

# Mendaftarkan router dari auth.py
app.include_router(auth_router)
app.include_router(destinasi_router)
app.include_router(paket_router)
app.include_router(blog_router)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Desa Wisata API"}
