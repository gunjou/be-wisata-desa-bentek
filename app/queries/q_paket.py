from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_connection


def get_all_paket():
    """Fungsi untuk mengambil semua paket wisata yang aktif"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.connect() as connection:
            # Query untuk mengambil semua paket wisata yang status = 1 (aktif)
            query = text("""
                SELECT id_package, name, description, price, destinations, benefits, image_url, created_at, updated_at
                FROM packages
                WHERE status = 1
                ORDER BY created_at DESC;
            """)

            result = connection.execute(query).mappings().fetchall()

            if result:
                # Mengembalikan data paket wisata dalam bentuk list of dictionaries
                return [
                    {
                        "id_package": row["id_package"],
                        "name": row["name"],
                        "description": row["description"],
                        "price": row["price"],
                        "destinations": row["destinations"],  # Array of destinations
                        "benefits": row["benefits"],          # Array of benefits
                        "image_url": row["image_url"],
                        "created_at": str(row["created_at"]),
                        "updated_at": str(row["updated_at"]),
                    }
                    for row in result
                ]
            return []  # Mengembalikan list kosong jika tidak ada paket wisata
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None

def get_package_by_id(package_id: int):
    """Fungsi untuk mengambil paket wisata berdasarkan ID"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.connect() as connection:
            # Query untuk mengambil detail paket wisata berdasarkan ID
            query = text("""
                SELECT id_package, name, description, price, destinations, benefits, image_url, created_at, updated_at
                FROM packages
                WHERE id_package = :id_package AND status = 1
                LIMIT 1;
            """)

            result = connection.execute(query, {"id_package": package_id}).mappings().fetchone()

            if result:
                # Mengembalikan data paket wisata dalam bentuk dictionary
                return {
                    "id_package": result["id_package"],
                    "name": result["name"],
                    "description": result["description"],
                    "price": result["price"],
                    "destinations": result["destinations"],  # Array of destination IDs
                    "benefits": result["benefits"],          # Array of benefits
                    "image_url": result["image_url"],
                    "created_at": str(result["created_at"]),
                    "updated_at": str(result["updated_at"]),
                }
            return None  # Jika paket tidak ditemukan
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def add_package(name: str, description: str, price: float, destinations: list, benefits: list, image_url: str):
    """Fungsi untuk menambah paket wisata baru ke dalam database"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                INSERT INTO packages (name, description, price, destinations, benefits, image_url, status, created_at, updated_at)
                VALUES (:name, :description, :price, :destinations, :benefits, :image_url, 1, NOW(), NOW())
                RETURNING id_package, name, description, price, destinations, benefits, image_url, created_at, updated_at;
            """)

            # Menambahkan .mappings() untuk memastikan hasil bisa diakses dengan nama kolom
            result = connection.execute(query, {
                "name": name,
                "description": description,
                "price": price,
                "destinations": destinations,
                "benefits": benefits,
                "image_url": image_url
            }).mappings().fetchone()  # Mengambil hasil satu baris hasil eksekusi query

            if result:
                # Mengakses hasil menggunakan nama kolom
                return {
                    "id_package": result["id_package"],
                    "name": result["name"],
                    "description": result["description"],
                    "price": result["price"],
                    "destinations": result["destinations"],
                    "benefits": result["benefits"],
                    "image_url": result["image_url"],
                    "created_at": str(result["created_at"]),
                    "updated_at": str(result["updated_at"]),
                }
            return None  # Jika gagal menambah paket
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def update_package(package_id: int, name: str, description: str, price: float, destinations: list, benefits: list, image_url: str):
    """Fungsi untuk mengupdate paket wisata berdasarkan ID"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                UPDATE packages
                SET name = COALESCE(:name, name),
                    description = COALESCE(:description, description),
                    price = COALESCE(:price, price),
                    destinations = COALESCE(:destinations, destinations),
                    benefits = COALESCE(:benefits, benefits),
                    image_url = COALESCE(:image_url, image_url),
                    updated_at = NOW()
                WHERE id_package = :id_package
                RETURNING id_package, name, description, price, destinations, benefits, image_url, created_at, updated_at;
            """)

            # Menjalankan query dengan parameter
            result = connection.execute(query, {
                "id_package": package_id,
                "name": name,
                "description": description,
                "price": price,
                "destinations": destinations,
                "benefits": benefits,
                "image_url": image_url
            }).mappings().fetchone()  # Mengambil hasil satu baris hasil eksekusi query

            if result:
                # Mengembalikan hasil query dalam bentuk dictionary
                return {
                    "id_package": result["id_package"],
                    "name": result["name"],
                    "description": result["description"],
                    "price": result["price"],
                    "destinations": result["destinations"],
                    "benefits": result["benefits"],
                    "image_url": result["image_url"],
                    "created_at": str(result["created_at"]),
                    "updated_at": str(result["updated_at"]),
                }
            return None  # Jika gagal mengupdate paket
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None
    
def soft_delete_package(package_id: int):
    """Fungsi untuk melakukan soft delete (mengubah status menjadi 0) pada paket wisata"""
    conn = get_connection()  # Membuka koneksi ke database
    try:
        with conn.begin() as connection:  # Memulai transaksi untuk operasi yang memerlukan commit
            query = text("""
                UPDATE packages
                SET status = 0, updated_at = NOW()
                WHERE id_package = :id_package
                RETURNING id_package, name, description, price, destinations, benefits, image_url, created_at, updated_at, status;
            """)

            # Menjalankan query dengan parameter
            result = connection.execute(query, {"id_package": package_id}).mappings().fetchone()

            if result:
                # Mengembalikan hasil query dalam bentuk dictionary
                return {
                    "id_package": result["id_package"],
                    "name": result["name"],
                }
            return None  # Jika gagal melakukan soft delete
    except SQLAlchemyError as e:
        print(f"Database error occurred: {str(e)}")
        return None