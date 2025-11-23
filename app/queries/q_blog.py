from typing import Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_connection


def get_all_blogs():
    """Fungsi untuk mengambil semua blog dengan status aktif"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.connect() as connection:
            query = text("""
                SELECT id_blog, title, content, image_url, post_url, created_at, updated_at
                FROM blogs
                WHERE status = 1
                ORDER BY created_at DESC;
            """)

            result = connection.execute(query).mappings().fetchall()

            if result:
                return [
                    {
                        "id_blog": row["id_blog"],
                        "title": row["title"],
                        "content": row["content"],
                        "image_url": row["image_url"],
                        "post_url": row["post_url"],
                        "created_at": str(row["created_at"]),
                        "updated_at": str(row["updated_at"]),
                    }
                    for row in result
                ]
            return []
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None

def get_blog_by_id(blog_id: int):
    conn = get_connection()
    try:
        with conn.connect() as connection:
            query = text("""
                SELECT id_blog, title, content, image_url, post_url, created_at, updated_at
                FROM blogs
                WHERE id_blog = :id_blog AND status = 1
                LIMIT 1;
            """)

            result = connection.execute(query, {"id_blog": blog_id}).mappings().fetchone()

            if result:
                return {
                    "id_blog": result["id_blog"],
                    "title": result["title"],
                    "content": result["content"],
                    "image_url": result["image_url"],
                    "post_url": result["post_url"],
                    "created_at": str(result["created_at"]),
                    "updated_at": str(result["updated_at"]),
                }
            return None
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def add_blog(title: str, content: str, image_url: Optional[str], post_url: Optional[str]):
    """Fungsi untuk menambah blog baru ke database"""
    conn = get_connection()
    try:
        with conn.begin() as connection:
            query = text("""
                INSERT INTO blogs (title, content, image_url, post_url, status, created_at, updated_at)
                VALUES (:title, :content, :image_url, :post_url, 1, NOW(), NOW())
                RETURNING id_blog, title, content, image_url, post_url, created_at, updated_at;
            """)

            result = connection.execute(query, {
                "title": title,
                "content": content,
                "image_url": image_url,
                "post_url": post_url
            }).fetchone()

            if result:
                return {
                    "id_blog": result[0],
                    "title": result[1],
                    "content": result[2],
                    "image_url": result[3],
                    "post_url": result[4],
                    "created_at": str(result[5]),
                    "updated_at": str(result[6]),
                }
            return None
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def update_blog(blog_id: int, title: str, content: str, image_url: Optional[str], post_url: Optional[str]):
    """Fungsi untuk mengupdate blog ke database"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                UPDATE blogs
                SET title = COALESCE(:title, title),
                    content = COALESCE(:content, content),
                    image_url = COALESCE(:image_url, image_url),
                    post_url = COALESCE(:post_url, post_url),
                    updated_at = NOW()
                WHERE id_blog = :id_blog
                RETURNING id_blog, title, content, image_url, post_url, created_at, updated_at;
            """)

            result = connection.execute(query, {
                "id_blog": blog_id,
                "title": title,
                "content": content,
                "image_url": image_url,
                "post_url": post_url
            }).fetchone()  # Mengambil hasil satu baris hasil eksekusi query

            if result:
                # Mengembalikan hasil dalam bentuk dictionary
                return {
                    "id_blog": result[0],
                    "title": result[1],
                    "content": result[2],
                    "image_url": result[3],
                    "post_url": result[4],
                    "created_at": str(result[5]),
                    "updated_at": str(result[6]),
                }
            return None  # Jika gagal
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def soft_delete_blog(blog_id: int):
    """Fungsi untuk melakukan soft delete (mengubah status menjadi 0) pada blog"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                UPDATE blogs
                SET status = 0, updated_at = NOW()
                WHERE id_blog = :id_blog
                RETURNING id_blog, title;
            """)

            # Menjalankan query dengan parameter
            result = connection.execute(query, {"id_blog": blog_id}).mappings().fetchone()

            if result:
                # Mengembalikan hasil query dalam bentuk dictionary
                return {
                    "id_blog": result["id_blog"],
                    "title": result["title"],
                }
            return None  # Jika gagal melakukan soft delete
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None