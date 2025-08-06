# backend/app.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, current_app, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from backend.models import User, Container
from backend.config import Config
from backend.services.docker_service import DockerService
from backend.database import db, migrate

# Ensure that the models are imported so Alembic can detect them
# This is a crucial step for migrations to work correctly.
# from models import User, Container

# Initialize JWT Manager
jwt = JWTManager()

def create_app(config_class=Config):
    # Create the Flask application instance
    app = Flask(__name__)

    # Load configuration from the Config object
    app.config.from_object(config_class)

    # Enable CORS for frontend communication
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3002"}})

    # Initialize extensions with the app instance
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Configure logging for the application
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/platform_saas.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Platform SaaS application started.')
    
    # Initialize the Docker service
    try:
        app.docker_service = DockerService(app_logger=app.logger, docker_host_uri=app.config.get('DOCKER_HOST_URI'))
        if not app.docker_service.client:
            app.logger.error("Docker client failed to initialize. Container management will not be available.")
    except Exception as e:
        app.logger.critical(f"Error during DockerService initialization: {e}", exc_info=True)
        app.docker_service = None

    # Import and register blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.container_routes import container_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(container_bp, url_prefix='/api/containers')

    # Basic root route for health check
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Platform SaaS API! The server is running."}), 200

    # Error handling routes
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Resource not found: {request.path}")
        return jsonify({"error": "Not Found", "message": "The requested resource does not exist."}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.critical(f"Internal server error: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "An unexpected server error occurred."}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)