from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from .utils.config import validate_jwt_token
from .queries.q_paket import *

router = APIRouter()

# Pydantic model untuk response paket wisata
class PaketResponse(BaseModel):
    id_package: int
    name: str
    description: str
    price: Optional[float] = None
    destinations: Optional[List[int]] = []  # Array of destination IDs
    benefits: Optional[List[str]] = []      # Array of benefits
    image_url: Optional[str] = None
    created_at: str
    updated_at: str
    
# Pydantic model untuk validasi input data paket wisata
class PaketCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    destinations: List[int]  # Array of destination IDs
    benefits: Optional[List[str]] = []  # Array of benefits
    image_url: Optional[str] = None
    
# Pydantic model untuk update data paket wisata
class PackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    destinations: Optional[List[int]] = None  # Daftar ID destinasi yang terkait
    benefits: Optional[List[str]] = None  # Daftar benefits paket
    image_url: Optional[str] = None


@router.get("/paket", response_model=List[PaketResponse], tags=["Paket"])
async def get_paket():
    """Endpoint untuk menampilkan semua paket wisata"""
    paket = get_all_paket()
    if paket is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    if not paket:
        return []  # Jika tidak ada paket, kembalikan list kosong
    return paket

@router.get("/paket/{id}", response_model=PaketResponse, tags=["Paket"])
async def get_package(id: int):
    """Endpoint untuk menampilkan detail paket berdasarkan ID"""
    paket = get_package_by_id(id)
    if paket is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return paket

@router.post("/paket", response_model=PaketResponse, tags=["Paket"])
async def create_package(paket_create: PaketCreate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menambah paket wisata baru"""
    # Panggil fungsi query untuk menambah paket wisata
    new_package = add_package(
        paket_create.name,
        paket_create.description,
        paket_create.price,
        paket_create.destinations,
        paket_create.benefits,
        paket_create.image_url
    )
    if not new_package:
        raise HTTPException(status_code=400, detail="Failed to add package")
    return new_package  # Mengembalikan paket wisata yang baru ditambahkan

@router.put("/paket/{id}", response_model=PaketResponse, tags=["Paket"])
async def update_package_endpoint(id: int, package_update: PackageUpdate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk mengedit paket wisata berdasarkan ID"""
    updated_package = update_package(
        package_id=id,
        name=package_update.name,
        description=package_update.description,
        price=package_update.price,
        destinations=package_update.destinations,
        benefits=package_update.benefits,
        image_url=package_update.image_url
    )
    if not updated_package:
        raise HTTPException(status_code=400, detail="Failed to update package")
    return updated_package  # Mengembalikan paket yang sudah diperbarui

@router.delete("/paket/{id}", tags=["Paket"])
async def delete_package(id: int, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menghapus paket wisata berdasarkan ID (Soft Delete)"""
    # Panggil fungsi query untuk melakukan soft delete
    deleted_package = soft_delete_package(package_id=id)
    if not deleted_package:
        raise HTTPException(status_code=400, detail="Failed to delete package")
    return {"message": f"Paket '{deleted_package['name']}' deleted successfully"}