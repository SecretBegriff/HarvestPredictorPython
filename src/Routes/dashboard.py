from flask import Blueprint, jsonify
from src.DataBase.modules.sensor_reading_module import SensorRepository

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/python')
sensor_repo = SensorRepository()

# ESTA ES LA RUTA QUE TU JS LLAMARÁ
@dashboard_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    try:
        # Obtiene la última lectura de cada planta
        results = sensor_repo.get_dashboard_last_readings()
        
        # Formateo de fechas para JSON
        for result in results:
            if result.get('reading_timestamp'):
                result['reading_timestamp'] = result['reading_timestamp'].isoformat()
        
        return jsonify({'status': 'success', 'data': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
        