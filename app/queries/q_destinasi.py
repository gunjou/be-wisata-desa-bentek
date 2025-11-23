from typing import Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_connection


def get_all_destinations():
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.connect() as connection:
            # Query untuk mengambil semua destinasi yang status = 1 (aktif)
            query = text("""
                SELECT id_destination, name, description, image_url, location_url, created_at, updated_at
                FROM destinations
                WHERE status = 1
                ORDER BY created_at DESC;
            """)

            result = connection.execute(query).mappings().fetchall()

            if result:
                # Mengembalikan data destinasi dalam bentuk list of dictionaries
                return [
                    {
                        "id_destination": row["id_destination"],
                        "name": row["name"],
                        "description": row["description"],
                        "image_url": row["image_url"],
                        "location_url": row["location_url"],
                        "created_at": str(row["created_at"]),
                        "updated_at": str(row["updated_at"]),
                    }
                    for row in result
                ]
            return []  # Mengembalikan list kosong jika tidak ada destinasi
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None

def get_destination_by_id(destination_id: int):
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.connect() as connection:
            # Query untuk mengambil destinasi berdasarkan ID
            query = text("""
                SELECT id_destination, name, description, image_url, location_url, created_at, updated_at
                FROM destinations
                WHERE id_destination = :id_destination AND status = 1
                LIMIT 1;
            """)

            result = connection.execute(query, {"id_destination": destination_id}).mappings().fetchone()

            if result:
                # Mengembalikan data destinasi dalam bentuk dictionary
                return {
                    "id_destination": result["id_destination"],
                    "name": result["name"],
                    "description": result["description"],
                    "image_url": result["image_url"],
                    "location_url": result["location_url"],
                    "created_at": str(result["created_at"]),
                    "updated_at": str(result["updated_at"]),
                }
            return None  # Jika destinasi tidak ditemukan
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def add_destination(name: str, description: str, image_url: str, location_url: str):
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                INSERT INTO destinations (name, description, image_url, location_url, status, created_at, updated_at)
                VALUES (:name, :description, :image_url, :location_url, 1, NOW(), NOW())
                RETURNING id_destination, name, description, image_url, location_url, created_at, updated_at;
            """)
            
            result = connection.execute(query, {
                "name": name,
                "description": description,
                "image_url": image_url,
                "location_url": location_url
            }).fetchone()

            if result:
                return {
                    "id_destination": result[0],
                    "name": result[1],
                    "description": result[2],
                    "image_url": result[3],
                    "location_url": result[4],
                    "created_at": str(result[5]),
                    "updated_at": str(result[6]),
                }
            return None
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def update_destination(destination_id: int, name: Optional[str], description: Optional[str], image_url: Optional[str], location_url: Optional[str]):
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:
            query = text("""
                UPDATE destinations
                SET name = COALESCE(:name, name),
                    description = COALESCE(:description, description),
                    image_url = COALESCE(:image_url, image_url),
                    location_url = COALESCE(:location_url, location_url),
                    updated_at = NOW()
                WHERE id_destination = :id_destination
                RETURNING id_destination, name, description, image_url, location_url, created_at, updated_at;
            """)

            result = connection.execute(query, {
                "id_destination": destination_id,
                "name": name,
                "description": description,
                "image_url": image_url,
                "location_url": location_url
            }).fetchone()

            if result:
                return {
                    "id_destination": result[0],
                    "name": result[1],
                    "description": result[2],
                    "image_url": result[3],
                    "location_url": result[4],
                    "created_at": str(result[5]),
                    "updated_at": str(result[6]),
                }
            return None
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def soft_delete_destination(destination_id: int):
    """Fungsi untuk melakukan soft delete destinasi dengan mengubah status menjadi 0"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:
            query = text("""
                UPDATE destinations
                SET status = 0, updated_at = NOW()
                WHERE id_destination = :id_destination
                RETURNING id_destination, name;
            """)
            
            result = connection.execute(query, {"id_destination": destination_id}).fetchone()

            if result:
                # Mengembalikan data destinasi yang diupdate
                return {
                    "id_destination": result[0],
                    "name": result[1]
                }
            return None  # Jika destinasi tidak ditemukan atau gagal
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None