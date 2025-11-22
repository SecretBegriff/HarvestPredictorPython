from flask import Blueprint, jsonify
from src.DataBase.modules.plant_module import PlantRepository

plants_bp = Blueprint('plants', __name__, url_prefix='/api/python')
plant_repo = PlantRepository()

@plants_bp.route('/plants', methods=['GET'])
def get_plants():
    try:
        results = plant_repo.get_all_plants()
        # Formateo de fechas
        for result in results:
            if result.get('planting_date'):
                result['planting_date'] = result['planting_date'].isoformat().split('T')[0]
        return jsonify({'status': 'success', 'data': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

        