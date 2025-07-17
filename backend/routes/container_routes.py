# backend/routes/container_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from docker.errors import NotFound, APIError
from typing import Dict, Any, Optional # Ajout des imports de typage

from ..models import Container, User, db
from ..schemas import container_create_schema, container_schema, containers_schema
from ..services.docker_service import DockerService # Ajout de l'import pour le type hint

container_bp = Blueprint('containers', __name__, url_prefix='/containers')

# Helper function to get the Docker service instance, which is stored on current_app
def get_docker_service() -> DockerService: # Ajout du type hint pour aider Pylance
    # Pylance peut se plaindre que 'docker_service' n'est pas un attribut de 'Flask'.
    # On l'ignore car il est défini dynamiquement dans app.py.
    return current_app.docker_service # type: ignore [attr-defined]

@container_bp.route('/', methods=['POST'])
@jwt_required()
def create_container():
    docker_service = get_docker_service()
    # Pylance peut toujours se plaindre de 'docker_service.client' si docker_service pourrait être None
    # On ajoute un type ignore ou on s'assure que get_docker_service ne retourne jamais None si le service est censé être toujours là
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    try:
        # Ajout du type hint pour container_data pour aider Pylance à comprendre que c'est un dictionnaire
        json_data = request.get_json()
        if json_data is None:
            return jsonify({"errors": {"_schema": ["Invalid JSON"]}}), 400

        container_data: Dict[str, Any] = container_create_schema.load(json_data) # type: ignore [assignment] # AJOUTÉ ICI : Pour les problèmes de typage avec Marshmallow
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    name = container_data['name']
    image = container_data['image']
    ports = container_data.get('ports') # Optional

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    try:
        docker_container_id = docker_service.create_and_run_container(
            name=name,
            image=image,
            ports=ports # String format like "8080:80/tcp"
        )
        if not docker_container_id:
            return jsonify({"msg": "Failed to create Docker container (no ID returned)"}), 500

        new_container = Container(
            user_id=user_id,
            name=name,
            image=image,
            docker_container_id=docker_container_id,
            status='running',
            ports=ports # Store the string representation
        )
        db.session.add(new_container)
        db.session.commit()

        return jsonify({"msg": "Container created successfully", "container": container_schema.dump(new_container)}), 201
    except ValidationError as e: # Catch ValueError from DockerService (e.g., invalid ports)
        current_app.logger.error(f"Validation error creating container: {e}") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"Validation error: {str(e)}"}), 400
    except APIError as e:
        current_app.logger.error(f"Docker API error in create_container route: {e}") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"Docker API error: {str(e)}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred in create_container route: {e}", exc_info=True) # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_id: str):
    docker_service = get_docker_service()
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    user_id = get_jwt_identity()
    container_db = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container_db:
        return jsonify({"msg": "Container not found or unauthorized"}), 404

    try:
        docker_service.start_container(container_id)
        container_db.status = 'running'
        db.session.commit()
        return jsonify({"msg": f"Container {container_id} started"}), 200
    except NotFound:
        current_app.logger.error(f"Container {container_id} not found on Docker daemon for start operation.") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": "Container not found on Docker daemon"}), 404
    except APIError as e:
        current_app.logger.error(f"Docker API error starting container {container_id}: {e}") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"Failed to start container: {str(e)}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred starting container {container_id}: {e}", exc_info=True) # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_id: str):
    docker_service = get_docker_service()
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    user_id = get_jwt_identity()
    container_db = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container_db:
        return jsonify({"msg": "Container not found or unauthorized"}), 404

    try:
        docker_service.stop_container(container_id)
        container_db.status = 'exited' # Or 'stopped' depending on your schema
        db.session.commit()
        return jsonify({"msg": f"Container {container_id} stopped"}), 200
    except NotFound:
        current_app.logger.error(f"Container {container_id} not found on Docker daemon for stop operation.") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": "Container not found on Docker daemon"}), 404
    except APIError as e:
        current_app.logger.error(f"Docker API error stopping container {container_id}: {e}") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"Failed to stop container: {str(e)}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred stopping container {container_id}: {e}", exc_info=True) # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/remove', methods=['DELETE'])
@jwt_required()
def remove_container(container_id: str):
    docker_service = get_docker_service()
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    user_id = get_jwt_identity()
    container_db = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container_db:
        return jsonify({"msg": "Container not found or unauthorized"}), 404

    try:
        docker_service.remove_container(container_id)
        db.session.delete(container_db) # Remove from your database as well
        db.session.commit()
        return jsonify({"msg": f"Container {container_id} removed"}), 200
    except NotFound:
        current_app.logger.error(f"Container {container_id} not found on Docker daemon for remove operation.") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": "Container not found on Docker daemon"}), 404
    except APIError as e:
        current_app.logger.error(f"Docker API error removing container {container_id}: {e}") # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"Failed to remove container: {str(e)}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred removing container {container_id}: {e}", exc_info=True) # type: ignore [attr-defined]
        db.session.rollback()
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500

@container_bp.route('/', methods=['GET'])
@jwt_required()
def list_user_containers():
    docker_service = get_docker_service()
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    user_id = get_jwt_identity()
    containers = Container.query.filter_by(user_id=user_id).all()

    return jsonify(containers_schema.dump(containers)), 200

@container_bp.route('/<string:container_id>/logs', methods=['GET'])
@jwt_required()
def get_container_logs_route(container_id: str):
    docker_service = get_docker_service()
    if not docker_service.client: # type: ignore [union-attr]
        return jsonify({"msg": "Docker service is not initialized or connected"}), 500

    user_id = get_jwt_identity()
    container_db = Container.query.filter_by(docker_container_id=container_id, user_id=user_id).first()
    if not container_db:
        return jsonify({"msg": "Container not found or unauthorized"}), 404

    try:
        logs = docker_service.get_container_logs(container_id)
        return jsonify({"logs": logs}), 200
    except NotFound:
        current_app.logger.error(f"Container {container_id} not found on Docker daemon for logs.") # type: ignore [attr-defined]
        return jsonify({"msg": "Container not found on Docker daemon"}), 404
    except APIError as e:
        current_app.logger.error(f"Docker API error getting logs for container {container_id}: {e}") # type: ignore [attr-defined]
        return jsonify({"msg": f"Failed to retrieve logs: {str(e)}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred getting logs for container {container_id}: {e}", exc_info=True) # type: ignore [attr-defined]
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500