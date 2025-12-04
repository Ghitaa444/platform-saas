import logging
import json
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Container
from database import db
from services.docker_service import DockerServiceException
from docker.errors import APIError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

container_bp = Blueprint("container_bp", __name__)


def ensure_docker_available():
    """Vérifie la disponibilité du client Docker."""
    if not current_app.docker_service or not current_app.docker_service.client:
        logger.error("❌ DockerService non initialisé ou client Docker non disponible.")
        return jsonify({"message": "Service Docker non disponible"}), 500
    return None


# -----------------------------------------------------------
# 🚀 Créer un container
# -----------------------------------------------------------
@container_bp.route("/create", methods=["POST"])
@jwt_required()
def create_container():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    data = request.get_json() or {}
    container_name = data.get("container_name")
    image_name = data.get("image_name")
    ports_list = data.get("ports", [])
    environment_data = data.get("environment", {})
    network = data.get("network")
    volumes = data.get("volumes", [])
    cpu_shares = data.get("cpu_shares")
    memory = data.get("memory")

    if not container_name or not image_name:
        return jsonify({"message": "Nom du conteneur et image requis"}), 400

    ports_dict, ports_for_db = {}, []
    for p in ports_list:
        try:
            host_port, container_port = p.split(":")
            ports_dict[f"{container_port}/tcp"] = int(host_port)
            ports_for_db.append(p)
        except ValueError:
            logger.warning(f"⚠️ Format de port invalide ignoré: {p}")

    environment_dict = environment_data if isinstance(environment_data, dict) else {}
    command_to_run = ["nginx", "-g", "daemon off;"] if image_name.startswith("nginx") else None

    error_response = ensure_docker_available()
    if error_response:
        return error_response

    if Container.query.filter_by(name=container_name, user_id=user.id).first():
        return jsonify({"message": f"Un conteneur '{container_name}' existe déjà."}), 409

    try:
        container_obj = current_app.docker_service.create_container(
            image=image_name,
            name=container_name,
            ports=ports_dict,
            environment=environment_dict,
            network=network,
            volumes=volumes,
            cpu_shares=cpu_shares,
            memory=memory,
            command=command_to_run,
        )

        docker_id = container_obj.id
        new_container = Container(
            docker_container_id=docker_id,
            name=container_name,
            image=image_name,
            status="running",
            user_id=user.id,
            ports=json.dumps(ports_for_db),
            environment=json.dumps(environment_dict),
        )
        db.session.add(new_container)
        db.session.commit()

        logger.info(f"✅ Conteneur '{container_name}' créé avec succès pour {user.username}")
        return jsonify({
            "message": "Conteneur créé avec succès",
            "container": {
                "docker_id": docker_id,
                "name": container_name,
                "image": image_name,
                "status": "running",
                "ports": ports_for_db,
                "environment": environment_dict
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        if 'docker_id' in locals():
            current_app.docker_service.delete_container(docker_id)
        return jsonify({"message": "Échec en base, conteneur supprimé"}), 409
    except (DockerServiceException, APIError, Exception) as e:
        db.session.rollback()
        logger.error(f"Erreur Docker lors de la création: {e}", exc_info=True)
        return jsonify({"message": f"Erreur lors de la création: {str(e)}"}), 500


# -----------------------------------------------------------
# ▶️ Démarrer un container
# -----------------------------------------------------------
@container_bp.route("/<string:container_id>/start", methods=["POST"])
@jwt_required()
def start_container(container_id):
    user_id = get_jwt_identity()
    container = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container:
        return jsonify({"message": "Conteneur non trouvé"}), 404

    error_response = ensure_docker_available()
    if error_response:
        return error_response

    try:
        current_app.docker_service.start_container(container_id)
        container.status = "running"
        db.session.commit()
        logger.info(f"▶️ Conteneur {container.name} démarré par {user_id}")
        return jsonify({"message": "Conteneur démarré"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur: {str(e)}"}), 500


# -----------------------------------------------------------
# ⏸️ Arrêter un container
# -----------------------------------------------------------
@container_bp.route("/<string:container_id>/stop", methods=["POST"])
@jwt_required()
def stop_container(container_id):
    user_id = get_jwt_identity()
    container = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container:
        return jsonify({"message": "Conteneur non trouvé"}), 404

    error_response = ensure_docker_available()
    if error_response:
        return error_response

    try:
        current_app.docker_service.stop_container(container_id)
        container.status = "exited"
        db.session.commit()
        logger.info(f"⏸️ Conteneur {container.name} arrêté par {user_id}")
        return jsonify({"message": "Conteneur arrêté"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur: {str(e)}"}), 500


# -----------------------------------------------------------
# 🗑️ Supprimer un container
# -----------------------------------------------------------
@container_bp.route("/<string:container_id>/remove", methods=["DELETE"])
@jwt_required()
def remove_container(container_id):
    user_id = get_jwt_identity()
    container = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container:
        return jsonify({"message": "Conteneur non trouvé"}), 404

    try:
        if current_app.docker_service:
            try:
                current_app.docker_service.delete_container(container_id)
            except APIError as e:
                logger.warning(f"Erreur lors de la suppression Docker: {e}")

        db.session.delete(container)
        db.session.commit()
        logger.info(f"🗑️ Conteneur {container.name} supprimé pour {user_id}")
        return jsonify({"message": "Conteneur supprimé"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression: {e}", exc_info=True)
        return jsonify({"message": f"Erreur: {str(e)}"}), 500


# -----------------------------------------------------------
# 📋 Lister les containers (DB + Docker + Stats CPU/RAM)
# -----------------------------------------------------------
@container_bp.route("/list", methods=["GET"])
@jwt_required()
def list_containers():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    try:
        db_containers = Container.query.filter_by(user_id=user.id).all()
        docker_containers = (
            current_app.docker_service.list_all_containers() if current_app.docker_service else []
        )

        docker_map = {c.get("Id", c.get("id")): c for c in docker_containers}
        results, to_remove = [], []

        for db_container in db_containers:
            docker_info = docker_map.get(db_container.docker_container_id)
            if docker_info:
                status = docker_info.get("Status", docker_info.get("status", "unknown"))
                image = docker_info.get("Image", db_container.image)
                ports = docker_info.get("Ports", docker_info.get("ports", []))

                # 🧠 Get CPU/RAM stats for each running container
                try:
                    stats = current_app.docker_service.get_container_stats(db_container.docker_container_id)
                    cpu = stats.get("cpu_percent", 0)
                    ram = stats.get("mem_percent", 0)
                except Exception:
                    cpu, ram = 0, 0
            else:
                status = "not found"
                image = db_container.image
                try:
                    ports = json.loads(db_container.ports or "[]")
                except Exception:
                    ports = []
                cpu, ram = 0, 0
                to_remove.append(db_container)

            try:
                env = json.loads(db_container.environment or "{}")
            except Exception:
                env = {}

            results.append({
                "id": db_container.id,
                "docker_id": db_container.docker_container_id,
                "name": db_container.name,
                "image": image,
                "status": status,
                "ports": ports,
                "environment": env,
                "cpu": round(cpu, 2),
                "ram": round(ram, 2),
            })

        if to_remove:
            for c in to_remove:
                db.session.delete(c)
            db.session.commit()
            logger.info(f"🧹 {len(to_remove)} conteneur(s) supprimé(s) de la DB (absents dans Docker).")

        return jsonify({"containers": results}), 200

    except Exception as e:
        logger.error(f"Erreur lors de list_containers: {e}", exc_info=True)
        return jsonify({"message": "Erreur interne du serveur"}), 500


# -----------------------------------------------------------
# 📊 Récupérer les stats CPU / RAM d’un container (unique)
# -----------------------------------------------------------
@container_bp.route("/<string:container_id>/stats", methods=["GET"])
@jwt_required()
def container_stats(container_id):
    """Retourne les statistiques CPU et RAM d’un conteneur Docker spécifique"""
    user_id = get_jwt_identity()

    container = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container:
        return jsonify({"message": "Conteneur non trouvé"}), 404

    error_response = ensure_docker_available()
    if error_response:
        return error_response

    try:
        stats = current_app.docker_service.get_container_stats(container_id)
        if not stats:
            return jsonify({"message": "Aucune donnée de stats"}), 404

        return jsonify(stats), 200

    except DockerServiceException as e:
        logger.error(f"Erreur DockerService pour {container_id}: {e}")
        return jsonify({"message": str(e)}), 500
    except Exception as e:
        logger.error(f"Erreur stats container {container_id}: {e}", exc_info=True)
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500
