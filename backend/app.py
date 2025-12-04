import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from models import User, Container
from config import Config
from services.docker_service import DockerService
from database import db, migrate


class CustomFlask(Flask):
    docker_service: DockerService | None = None


jwt = JWTManager()


def create_app(config_class=Config):
    app = CustomFlask(__name__)
    app.config.from_object(config_class)

    # ✅ CORS configuration (Codespaces, Docker, etc.)
    CORS(
        app,
        resources={r"/api/*": {"origins": ["https://*.app.github.dev"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Cache-Control"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # ✅ Gestion des requêtes OPTIONS (préflight)
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = jsonify({"status": "ok"})
            origin = request.headers.get("Origin")
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, Cache-Control"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response, 200

    # ✅ Headers CORS post-réponse
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and "app.github.dev" in origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, Cache-Control"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # 🔧 Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ✅ Logging configuration
    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/platform_saas.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Platform SaaS started")

    # ✅ Docker Service
    try:
        app.docker_service = DockerService(
            app_logger=app.logger,
            docker_host_uri=app.config.get("DOCKER_HOST_URI")
        )
        app.logger.info("Docker client connecté ✅")
    except Exception as e:
        app.logger.critical(f"Docker init error: {e}", exc_info=True)
        app.docker_service = None

    # ✅ Blueprints
    from routes.auth_routes import auth_bp
    from routes.container_routes import container_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(container_bp, url_prefix="/api/containers")

    # ✅ Healthcheck simple
    @app.route("/api/health", methods=["GET"])
    def health_check():
        docker_ok = app.docker_service is not None
        return jsonify({"status": "ok", "docker": docker_ok}), 200

    # 🏠 Route d’accueil
    @app.route("/")
    def home():
        return jsonify({"message": "Platform SaaS API running"}), 200

    return app


# ✅ Main entry
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
