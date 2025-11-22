import mysql.connector
from src.config import Config

def get_db_connection():
    """Crea y retorna una conexión a la base de datos."""
    return mysql.connector.connect(**Config.DB_CONFIG)