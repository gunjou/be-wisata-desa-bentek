from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from .utils.config import validate_jwt_token
from .queries.q_blog import *


router = APIRouter()

class BlogResponse(BaseModel):
    id_blog: int
    title: str
    content: str
    image_url: Optional[str] = None  # Nullable
    post_url: Optional[str] = None   # Nullable
    created_at: str
    updated_at: str

class BlogCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None  # Nullable
    post_url: Optional[str] = None
    
class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    post_url: Optional[str] = None


@router.get("/blog", response_model=List[BlogResponse], tags=["Blog"])
async def get_blogs():
    """Endpoint untuk menampilkan semua blog informasi"""
    blogs = get_all_blogs()
    if blogs is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    if not blogs:
        return []  # Jika tidak ada blog, kembalikan list kosong
    return blogs

@router.get("/blog/{id}", response_model=BlogResponse, tags=["Blog"])
async def get_blog(id: int):
    """Endpoint untuk menampilkan detail blog berdasarkan ID"""
    blog = get_blog_by_id(id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.post("/blog", response_model=BlogResponse, tags=["Blog"])
async def create_blog(blog_create: BlogCreate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menambah blog baru"""
    new_blog = add_blog(
        title=blog_create.title,
        content=blog_create.content,
        image_url=blog_create.image_url,
        post_url=blog_create.post_url
    )
    if not new_blog:
        raise HTTPException(status_code=400, detail="Failed to add blog")
    return new_blog

@router.put("/blog/{id}", response_model=BlogResponse, tags=["Blog"])
async def update_blog_endpoint(id: int, blog_update: BlogUpdate, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk mengedit blog wisata berdasarkan ID"""
    updated_blog = update_blog(
        blog_id=id,
        title=blog_update.title,
        content=blog_update.content,
        image_url=blog_update.image_url,
        post_url=blog_update.post_url
    )
    if not updated_blog:
        raise HTTPException(status_code=400, detail="Failed to update blog")
    return updated_blog  # Mengembalikan blog yang sudah diperbarui

@router.delete("/blog/{id}", tags=["Blog"])
async def delete_blog(id: int, token: str = Depends(validate_jwt_token)):
    """Endpoint untuk menghapus blog wisata berdasarkan ID (Soft Delete)"""
    # Panggil fungsi query untuk melakukan soft delete
    deleted_blog = soft_delete_blog(blog_id=id)
    if not deleted_blog:
        raise HTTPException(status_code=400, detail="Failed to delete blog")
    return {"message": f"Blog '{deleted_blog['title']}' deleted successfully"}