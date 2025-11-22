from src.database.db import get_db_connection

class UserRepository:

    def create_user(self, username, email, password_hash, phone_number=None):
        """
        Registra un nuevo usuario.
        NOTA: 'password_hash' ya debe venir encriptado desde el Servicio (Service Layer).
        No guardes contraseñas en texto plano.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO usuarios (username, email, password, phone_number, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """
        
        cursor.execute(query, (username, email, password_hash, phone_number))
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        return user_id

    def get_user_by_email(self, email):
        """
        Busca un usuario por su correo.
        Vital para el proceso de LOGIN.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios WHERE email = %s"
        
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return user

    def get_user_by_id(self, user_id):
        """
        Obtiene los datos de perfil de un usuario por su ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id, username, email, phone_number, created_at FROM usuarios WHERE id = %s"
        
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return user

    def get_users_for_alerts(self):
        """
        Obtiene la lista de usuarios que tienen número de celular registrado.
        Esta función la usará tu sistema de ALERTAS (Twilio/WhatsApp).
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Solo traemos usuarios que tengan un teléfono válido (NO NULL)
        query = """
        SELECT id, username, phone_number 
        FROM usuarios 
        WHERE phone_number IS NOT NULL AND phone_number != ''
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return results