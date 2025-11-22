from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar Blueprints
    from src.Routes.dashboard import dashboard_bp
    from src.Routes.plants import plants_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(plants_bp)

    return app