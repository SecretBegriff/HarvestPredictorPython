from flask import Flask, request, jsonify
from flask_cors import CORS
from conexion import tratarConexion
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
# Habilitamos CORS para permitir peticiones desde tu HTML (puerto 5500)
CORS(app)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    conn = None
    cursor = None
    try:
        if not request.is_json:
            return jsonify({"error": "Se requiere JSON"}), 400

        data = request.get_json()
        plant_name = data.get('plant', '').strip()
        
        if not plant_name:
            return jsonify({"error": "Nombre de planta no proporcionado"}), 400

        conn = tratarConexion()
        if conn is None:
            return jsonify({"error": "Fallo conexión BD"}), 500

        cursor = conn.cursor()

        # ---------------------------------------------------------
        # 1. CONSULTA DE DATOS ÓPTIMOS (Tabla: plant_types)
        # ---------------------------------------------------------
        sql_optimos = """
            SELECT id, optimal_temp, optimal_humidity
            FROM plant_types
            WHERE name = %s
            LIMIT 1
        """
        cursor.execute(sql_optimos, (plant_name,))
        row_opt = cursor.fetchone()
        
        if not row_opt:
            return jsonify({"error": f"La planta '{plant_name}' no existe en la base de datos"}), 404

        # Guardamos los óptimos
        # row_opt[0] es id, row_opt[1] es temp, row_opt[2] es humidity
        plant_type_id = row_opt[0] 
        optimal_temp = row_opt[1]
        optimal_humidity = row_opt[2]

        # ---------------------------------------------------------
        # 2. CONSULTA DE DATOS ACTUALES (Tabla: sensor_reading)
        # ---------------------------------------------------------
        # Lógica: 
        # Unimos (JOIN) sensor_reading con plants, y plants con plant_types.
        # Buscamos la lectura más reciente (ORDER BY reading_timestamp DESC)
        # que pertenezca al tipo de planta que buscamos.
        
        sql_sensores = """
            SELECT sr.temperature, sr.humidity
            FROM sensor_reading sr
            INNER JOIN plants p ON sr.plant_id = p.id
            INNER JOIN plant_types pt ON p.plant_type_id = pt.id
            WHERE pt.id = %s
            ORDER BY sr.reading_timestamp DESC
            LIMIT 1
        """
        
        cursor.execute(sql_sensores, (plant_type_id,))
        row_sensor = cursor.fetchone()

        if row_sensor:
            current_temp, current_humidity = row_sensor
        else:
            # Si la planta existe pero aun no tiene lecturas de sensores
            current_temp, current_humidity = None, None

        # ---------------------------------------------------------
        # 3. RESPUESTA AL FRONTEND
        # ---------------------------------------------------------
        response_data = {
            "optimal_temp": float(optimal_temp) if optimal_temp is not None else None,
            "optimal_humidity": float(optimal_humidity) if optimal_humidity is not None else None,
            "current_temp": float(current_temp) if current_temp is not None else None,
            "current_humidity": float(current_humidity) if current_humidity is not None else None
        }
        
        return jsonify(response_data)

    except mysql.connector.Error as db_err:
        print(f"Error BD: {db_err}")
        return jsonify({"error": f"Error de Base de Datos: {db_err}"}), 500
    except Exception as e:
        print(f"Error General: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
# --------------------------------------------------------------
# RUTA 2: Para llenar la pantalla "predictions.html"
# --------------------------------------------------------------
@app.route('/api/predictions-dashboard', methods=['GET'])
def get_dashboard_data():
    conn = tratarConexion()
    cursor = conn.cursor()
    
    try:
        # 1. OBTENER EL CULTIVO PRINCIPAL (El más reciente o activo)
        # Traemos también los 'harvest_days' que agregamos a la BD
        sql_main = """
            SELECT p.id, pt.name, p.planting_date, pt.harvest_days, pt.optimal_temp, pt.optimal_humidity
            FROM plants p
            JOIN plant_types pt ON p.plant_type_id = pt.id
            ORDER BY p.planting_date DESC
            LIMIT 1
        """
        cursor.execute(sql_main)
        row_plant = cursor.fetchone()
        
        if not row_plant:
            return jsonify({"error": "No hay plantas registradas"}), 404
            
        plant_id, name, planting_date, harvest_days, opt_temp, opt_hum = row_plant
        
        # 2. CÁLCULOS DE TIEMPO (Plant / Estimated days)
        # Si 'harvest_days' es None, usamos 90 por defecto
        ciclo_total = harvest_days if harvest_days else 90
        
        # Convertir a objeto fecha si es necesario
        if isinstance(planting_date, datetime): planting_date = planting_date.date()
        hoy = datetime.now().date()
        
        fecha_cosecha = planting_date + timedelta(days=ciclo_total)
        dias_restantes = (fecha_cosecha - hoy).days
        
        # Evitar números negativos si ya pasó la fecha
        if dias_restantes < 0: dias_restantes = 0

        # 3. DATOS DEL SENSOR (Factors & Main Prediction)
        sql_sensor = """
            SELECT temperature, humidity FROM sensor_reading 
            WHERE plant_id = %s 
            ORDER BY reading_timestamp DESC LIMIT 1
        """
        cursor.execute(sql_sensor, (plant_id,))
        row_sensor = cursor.fetchone()
        
        curr_temp = row_sensor[0] if row_sensor else 0
        curr_hum = row_sensor[1] if row_sensor else 0
        
        # Calculamos diferencias (Factores)
        diff_temp = round(curr_temp - opt_temp, 1) if curr_temp and opt_temp else 0
        diff_hum = round(curr_hum - opt_hum, 1) if curr_hum and opt_hum else 0

        # 4. DATOS PARA EL GRÁFICO (Distribución de plantas)
        sql_chart = """
            SELECT pt.name, COUNT(p.id) 
            FROM plants p 
            JOIN plant_types pt ON p.plant_type_id = pt.id 
            GROUP BY pt.name
        """
        cursor.execute(sql_chart)
        chart_data = cursor.fetchall() # [('Menta', 5), ('Girasol', 2)]

        # 5. CONSTRUIR EL JSON FINAL
        response = {
            "plant_name": name,
            "planting_date": str(planting_date),
            "harvest_date": fecha_cosecha.strftime("%b %d"), # Ej: "Nov 05"
            "days_left": dias_restantes,
            "total_cycle": ciclo_total,
            
            "factors": {
                "current_temp": curr_temp,
                "diff_temp": diff_temp, # Diferencia (+2 o -1)
                "current_hum": curr_hum,
                "diff_hum": diff_hum
            },
            
            "chart": {
                "labels": [row[0] for row in chart_data],
                "values": [row[1] for row in chart_data]
            },
            
            "status": "Riesgo" if abs(diff_temp) > 5 else "Saludable"
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
##Inicia Server
if __name__ == '__main__':
    app.run(debug=True, port=5000)