# backend/app.py

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from .config import Config, config_by_name # <-- MODIFIÉ : Importe config_by_name
from .services.docker_service import DockerService
from .database import db

# Charger les variables d'environnement depuis .env
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '.env'))

# Initialisation de JWTManager globalement
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    # Charger la configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default') 
    app.config.from_object(config_by_name[config_name]) 

    # Initialiser les extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Configuration du logger
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/platform_saas.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler) # type: ignore [attr-defined]

        app.logger.setLevel(logging.INFO) # type: ignore [attr-defined]
        app.logger.info('Démarrage de Platform SaaS') # type: ignore [attr-defined]

    # Ajout du service Docker à l'objet app
    try:
        app.docker_service = DockerService(app_logger=app.logger, docker_host_uri=app.config.get('DOCKER_HOST_URI')) # type: ignore [attr-defined]
        if not app.docker_service.client: # type: ignore [union-attr]
            app.logger.error("Le client Docker n'a pu s'initialiser. La gestion des conteneurs ne sera pas disponible.") # type: ignore [attr-defined]
        else:
            app.logger.info("Client Docker connecté et démon accessible!") # type: ignore [attr-defined]
    except Exception as e:
        app.logger.critical(f"Erreur lors de l'initialisation du DockerService: {e}") # type: ignore [attr-defined]
        app.docker_service = None # type: ignore [attr-defined]

    # Confirmer l'initialisation des composants
    app.logger.info("Base de données, JWT, Migrate et DockerService initialisés.") # type: ignore [attr-defined]

    # Enregistrement des Blueprints
    from backend.routes.user_routes import user_bp
    from backend.routes.auth_routes import auth_bp
    from backend.routes.container_routes import container_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(container_bp)

    # Route de test (peut être supprimée une fois les tests passés)
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to Platform SaaS API! Server is running."}), 200


    app.logger.info("Blueprints enregistrés.") # type: ignore [attr-defined]

    # Gestion globale des erreurs 404
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        pass
    app.run(host='0.0.0.0', port=5000, debug=True)