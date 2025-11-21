from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_connection, create_access_token


def add_admin(username, email, password):
    conn = get_connection()  # Membuka koneksi ke database
    try:
        # Hash password menggunakan werkzeug.security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Menggunakan begin() untuk transaksi yang memerlukan commit
        with conn.begin() as connection:
            query = text("""
                INSERT INTO users (username, email, password, role, status, created_at, updated_at)
                VALUES (:username, :email, :password, 'admin', 1, NOW(), NOW())
                RETURNING id_user, username, email, role, status, created_at, updated_at;
            """)
            
            # Menjalankan query dengan parameter, menggunakan hashed password
            result = connection.execute(query, {
                "username": username,
                "email": email,
                "password": hashed_password
            }).fetchone()  # Mengambil hasil satu baris hasil eksekusi query

            if result:
                # Mengembalikan data hasil query dalam bentuk dictionary
                return {
                    "id_user": result[0],
                    "username": result[1],
                    "email": result[2],
                    "role": result[3],
                    "status": result[4],
                    "created_at": result[5],
                    "updated_at": result[6],
                }
            return None
    except SQLAlchemyError as e:
        # Menangani error jika terjadi masalah pada query
        print(f"Database error occurred: {str(e)}")
        return None

# Fungsi login yang akan memverifikasi email dan password
def get_login(payload):
    conn = get_connection()
    try:
        with conn.connect() as connection:
            # Ambil user berdasarkan email
            result = connection.execute(
                text("""
                    SELECT id_user, username, email, password, role, status
                    FROM users
                    WHERE email = :email
                      AND status = 1
                    LIMIT 1;
                """),
                {"email": payload['email']}
            ).mappings().fetchone()
            
            # Cek password
            if result and result['password']:
                if check_password_hash(result['password'], payload['password']):
                    # Buat token JWT
                    access_token = create_access_token(
                        data={"sub": str(result['id_user']), "role": result['role']}
                    )
                    return {
                        'access_token': access_token,
                        'id_user': result['id_user'],
                        'name': result['username'],
                        'email': result['email'],
                        'role': result['role'],
                    }
            return None
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None