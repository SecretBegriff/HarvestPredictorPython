from src.DataBase.db import get_db_connection

class PlantRepository:
    
    def get_all_plants(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # CORREGIDO: Se eliminó la coma extra antes del FROM
        query = """
        SELECT 
            p.id, 
            p.planting_date, 
            pt.name AS plant_name, 
            pt.optimal_temp_min, 
            pt.optimal_temp_max, 
            pt.optimal_humidity_min,
            pt.optimal_humidity_max
        FROM plants p
        JOIN plant_types pt ON p.plant_type_id = pt.id
        ORDER BY p.id DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def create_plant(self, plant_type_id, planting_date):
        # Este método estaba bien, no requiere cambios
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO plants (plant_type_id, planting_date) VALUES (%s, %s)"
        
        cursor.execute(query, (plant_type_id, planting_date))
        conn.commit()
        plant_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return plant_id

    def get_plant_types(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # CORREGIDO: 
        # 1. Se eliminaron los 'pt.' (no son necesarios si solo consultas una tabla y no definiste el alias en el FROM).
        # 2. Se eliminó la coma extra antes del FROM.
        query = """
        SELECT 
            id, 
            name, 
            optimal_temp_min, 
            optimal_temp_max, 
            optimal_humidity_min, 
            optimal_humidity_max 
        FROM plant_types 
        ORDER BY name ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    # CORREGIDO: Ahora recibe los 5 argumentos necesarios (min y max)
    def create_plant_type(self, name, temp_min, temp_max, hum_min, hum_max):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # CORREGIDO: 
        # 1. Se eliminaron los 'pt.' (ilegal en INSERT).
        # 2. Se eliminó la coma extra al final de la lista de columnas.
        # 3. Se agregaron los placeholders correctos (%s) para los 5 valores.
        query = """
        INSERT INTO plant_types 
        (name, optimal_temp_min, optimal_temp_max, optimal_humidity_min, optimal_humidity_max) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Pasamos los 5 valores a la query
        cursor.execute(query, (name, temp_min, temp_max, hum_min, hum_max))
        conn.commit()
        type_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return type_id

    