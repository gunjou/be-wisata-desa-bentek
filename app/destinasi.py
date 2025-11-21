# app/destinasi.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from .queries.q_destinasi import *
from .utils.config import validate_jwt_token


router = APIRouter()

# Pydantic model untuk validasi input data destinasi
class DestinationCreate(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    
# Pydantic model untuk response
class DestinationResponse(BaseModel):
    id_destination: int
    name: str
    description: str
    image_url: Optional[str] = None  # Nullable
    created_at: str
    updated_at: str
    
# Pydantic model untuk validasi update data destinasi
class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    

@router.get("/destinasi", response_model=List[DestinationResponse], tags=["Destinasi"])
async def get_destinations():
    """Endpoint untuk menampilkan semua destinasi wisata"""
    destinations = get_all_destinations()

    if destinations is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if not destinations:
        return []  # Jika tidak ada destinasi, kembalikan list kosong

    return destinations


@router.get("/destinasi/{id}", response_model=DestinationResponse, tags=["Destinasi"])
async def get_destination(id: int):
    """Endpoint untuk menampilkan detail destinasi berdasarkan ID"""
    destination = get_destination_by_id(id)

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    return destination


@router.post("/destinasi", response_model=DestinationResponse, tags=["Destinasi"])
async def create_destination(destination: DestinationCreate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menambah destinasi baru"""
    new_destination = add_destination(destination.name, destination.description, destination.image_url)
    
    if not new_destination:
        raise HTTPException(status_code=400, detail="Failed to add destination")
    
    return new_destination  # Return the newly added destination


@router.put("/destinasi/{id}", response_model=DestinationResponse, tags=["Destinasi"])
async def update_destination_endpoint(id: int, destination_update: DestinationUpdate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk mengedit destinasi berdasarkan ID"""
    # Panggil fungsi query untuk melakukan update data destinasi
    updated_destination = update_destination(
        destination_id=id,
        name=destination_update.name,
        description=destination_update.description,
        image_url=destination_update.image_url
    )
    
    if not updated_destination:
        raise HTTPException(status_code=400, detail="Failed to update destination")
    
    return updated_destination  # Mengembalikan destinasi yang telah diupdate


@router.delete("/destinasi/{id}", tags=["Destinasi"])
async def delete_destination(id: int, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menghapus destinasi dengan soft delete (mengubah status menjadi 0)"""
    
    # Panggil fungsi untuk melakukan soft delete
    deleted_destination = soft_delete_destination(id)
    
    if not deleted_destination:
        raise HTTPException(status_code=404, detail="Destination not found or already deleted")
    
    return {"message": f"Destination '{deleted_destination['name']}' deleted successfully"}