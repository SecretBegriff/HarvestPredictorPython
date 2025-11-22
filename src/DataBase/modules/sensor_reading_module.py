from src.DataBase.db import get_db_connection
from datetime import datetime

class SensorRepository:

    def get_dashboard_last_readings(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        WITH RankedReadings AS (
            SELECT 
                sr.id,
                sr.temperature,
                sr.humidity,
                sr.reading_timestamp,
                p.id as plant_id,
                pt.name as plant_name,  -- Aquí se llama plant_name
                pt.optimal_temp_min, 
                pt.optimal_temp_max, 
                pt.optimal_humidity_min,
                pt.optimal_humidity_max,
                ROW_NUMBER() OVER(PARTITION BY sr.plant_id ORDER BY sr.reading_timestamp DESC) as rn
            FROM sensor_reading sr
            JOIN plants p ON sr.plant_id = p.id
            JOIN plant_types pt ON p.plant_type_id = pt.id
        )
        SELECT 
            plant_id,
            
            -- 1. CORRECCIÓN: Renombrar para coincidir con JS (plant_type_name)
            plant_name AS plant_type_name, 
            
            temperature, 
            humidity, 
            reading_timestamp,
            optimal_temp_min,
            optimal_temp_max,
            optimal_humidity_min,
            optimal_humidity_max,
            
            -- 2. CORRECCIÓN: Agregar Location (Hardcodeado por ahora)
            'Salon 212' AS location,

            -- 3. CORRECCIÓN: Renombrar status a sensor_status
            'Active' AS sensor_status
            
        FROM RankedReadings 
        WHERE rn = 1
        ORDER BY plant_id;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    # ... (El resto de tus funciones están correctas, no necesitan cambios)
    def get_plant_history(self, plant_id, limit=24):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT temperature, humidity, reading_timestamp
        FROM sensor_reading
        WHERE plant_id = %s
        ORDER BY reading_timestamp DESC
        LIMIT %s
        """
        
        cursor.execute(query, (plant_id, limit))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results[::-1]

    def add_reading(self, plant_id, temperature, humidity):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO sensor_reading (plant_id, temperature, humidity, reading_timestamp)
        VALUES (%s, %s, %s, NOW())
        """
        
        cursor.execute(query, (plant_id, temperature, humidity))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    def get_average_metrics(self, plant_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            AVG(temperature) as avg_temp, 
            AVG(humidity) as avg_hum,
            MIN(reading_timestamp) as first_reading,
            MAX(reading_timestamp) as last_reading,
            COUNT(*) as total_readings
        FROM sensor_reading
        WHERE plant_id = %s
        """
        
        cursor.execute(query, (plant_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result