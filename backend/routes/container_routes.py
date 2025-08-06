import logging
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, Container
from backend.database import db
from backend.services.docker_service import DockerServiceException
from docker.errors import APIError
from sqlalchemy.exc import IntegrityError
import json

logger = logging.getLogger(__name__)

container_bp = Blueprint('container_bp', __name__, url_prefix='/api/containers')

@container_bp.route('/create', methods=['POST'])
@jwt_required()
def create_container():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        logger.warning(f"Tentative de création de conteneur par utilisateur inconnu: {user_id}")
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Données JSON manquantes"}), 400

    # FIXED: Read keys that the frontend is actually sending
    container_name = data.get('container_name')
    image_name = data.get('image_name')
    
    # FIXED: Ports are sent as a list, but docker-py expects a dictionary.
    # Convert the list to the correct dictionary format.
    ports_list = data.get('ports', [])
    ports_dict = {}
    ports_for_db = [] # This will be the list of strings for the database

    for p in ports_list:
        try:
            host_port, container_port = p.split(':')
            ports_dict[f"{container_port}/tcp"] = int(host_port)
            ports_for_db.append(p)
        except (ValueError, IndexError):
            logger.warning(f"Format de port invalide dans la requête: {p}. Ignoré.")
    
    # FIXED: Ensure environment is a dictionary for the Docker service call.
    environment_data = data.get('environment', {})
    if isinstance(environment_data, str):
        environment_dict = {}
    elif isinstance(environment_data, dict):
        environment_dict = environment_data
    else:
        environment_dict = {}

    network = data.get('network')
    volumes = data.get('volumes', [])
    cpu_shares = data.get('cpu_shares')
    memory = data.get('memory')
    
    command_to_run = None
    if image_name and image_name.startswith('nginx'):
        command_to_run = ["nginx", "-g", "daemon off;"]

    if not image_name or not container_name:
        logger.warning(f"Requête invalide pour la création de conteneur par {user.username}: image_name ou container_name manquant")
        return jsonify({"message": "Nom de l'image et nom du conteneur sont requis"}), 400

    if not current_app.docker_service or not current_app.docker_service.client:
        logger.error("DockerService non initialisé ou client Docker non disponible.")
        return jsonify({"message": "Service Docker non disponible"}), 500

    try:
        # Check if a container with that name already exists for the user in the database
        existing_container_db = Container.query.filter_by(name=container_name, user_id=user.id).first()
        if existing_container_db:
            logger.warning(f"Tentative de création d'un conteneur en double: {container_name} pour utilisateur {user.username}")
            return jsonify({"message": f"Un conteneur avec le nom '{container_name}' existe déjà pour cet utilisateur."}), 409

        # Call Docker service to create the container with the corrected data
        container_obj = current_app.docker_service.create_container(
            image=image_name,
            name=container_name,
            ports=ports_dict,  # FIXED: Use the corrected ports dictionary
            environment=environment_dict, # FIXED: Use the corrected environment dictionary
            network=network,
            volumes=volumes,
            cpu_shares=cpu_shares,
            memory=memory,
            command=command_to_run
        )
        
        docker_container_id = container_obj.id
        docker_container_name = container_obj.name
        docker_container_status = 'created'

        if not docker_container_id:
            logger.error(f"Échec de la création du conteneur Docker pour {user.username}: {container_name} - Pas d'ID Docker retourné.")
            return jsonify({"message": "Échec de la création du conteneur Docker (pas d'ID retourné)"}), 500

        try:
            # Create a new database record
            new_container = Container(
                docker_container_id=docker_container_id,
                name=docker_container_name,
                image=image_name,
                status=docker_container_status,
                user_id=user.id,
                # FIXED: Use the list of ports for the database
                ports=json.dumps(ports_for_db),
                environment=json.dumps(environment_dict)
            )
            db.session.add(new_container)
            db.session.commit()

            logger.info(f"Conteneur '{docker_container_name}' créé avec succès pour l'utilisateur {user.username}. Docker ID: {docker_container_id}")
            return jsonify({
                "message": "Conteneur créé avec succès et enregistré en base de données",
                "container": {
                    "id": new_container.id,
                    "docker_id": new_container.docker_container_id,
                    "name": new_container.name,
                    "image": new_container.image,
                    "status": new_container.status,
                    "user_id": new_container.user_id,
                    "ports": json.loads(new_container.ports) if new_container.ports else [],
                    "environment": json.loads(new_container.environment) if new_container.environment else {}
                }
            }), 201
        
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Erreur de contrainte d'unicité lors de l'enregistrement en DB. Tentative de suppression du conteneur Docker: {container_name} (ID: {docker_container_id}).")
            try:
                current_app.docker_service.delete_container(docker_container_id)
                return jsonify({"message": f"Conteneur créé dans Docker, mais échec de l'enregistrement en base de données car un conteneur du même nom existe déjà. Le conteneur a été supprimé de Docker."}), 409
            except Exception as delete_error:
                logger.error(f"Échec de la suppression du conteneur Docker après une erreur de base de données. Erreur: {str(delete_error)}", exc_info=True)
                return jsonify({"message": f"Conteneur créé dans Docker, mais échec de l'enregistrement en base de données. Échec de la suppression du conteneur de Docker. Veuillez le supprimer manuellement."}), 500
        
        except Exception as db_error:
            db.session.rollback()
            logger.critical(f"Erreur CRITIQUE lors de l'enregistrement en BD. Tentative de suppression du conteneur Docker: {container_name} (ID: {docker_container_id}). Erreur: {str(db_error)}", exc_info=True)
            try:
                current_app.docker_service.delete_container(docker_container_id)
                return jsonify({"message": f"Conteneur créé dans Docker, mais échec de l'enregistrement en base de données. Le conteneur a été supprimé. Erreur: {str(db_error)}"}), 500
            except Exception as delete_error:
                logger.error(f"Échec de la suppression du conteneur Docker après une erreur de base de données. Erreur: {str(delete_error)}", exc_info=True)
                return jsonify({"message": f"Conteneur créé dans Docker, mais échec de l'enregistrement en base de données. Échec de la suppression du conteneur de Docker. Veuillez le supprimer manuellement."}), 500

    except APIError as e:
        db.session.rollback()
        if 'Conflict' in str(e) and 'container with that name already exists' in str(e):
            return jsonify({"message": f"Un conteneur avec le nom '{container_name}' existe déjà dans Docker. Veuillez en choisir un autre."}), 409
        else:
            logger.error(f"Erreur de l'API Docker lors de la création du conteneur: {e}", exc_info=True)
            return jsonify({"message": f"Erreur de l'API Docker: {str(e)}"}), 500
    
    except DockerServiceException as e:
        db.session.rollback()
        logger.error(f"Erreur du service Docker lors de la création du conteneur: {e}", exc_info=True)
        return jsonify({"message": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur inattendue lors de la création du conteneur pour l'utilisateur {user_id}: {e}", exc_info=True)
        return jsonify({"message": f"Erreur interne du serveur: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_id):
    user_id = get_jwt_identity()
    container = Container.query.filter_by(docker_container_id=container_id, user_id=int(user_id)).first()
    if not container:
        logger.warning(f"Tentative de démarrage de conteneur non autorisé ou inexistant: Docker ID={container_id}, UserID={user_id}")
        return jsonify({"message": "Conteneur non trouvé ou non autorisé"}), 404
    if not current_app.docker_service or not current_app.docker_service.client:
        logger.error("DockerService non initialisé ou client Docker non disponible.")
        return jsonify({"message": "Service Docker non disponible"}), 500
    try:
        current_app.docker_service.start_container(container_id)
        container.status = 'running'
        db.session.commit()
        if container.owner:
            logger.info(f"Conteneur '{container.name}' (Docker ID: {container_id}) démarré par l'utilisateur {container.owner.username}.")
        else:
            logger.info(f"Conteneur '{container.name}' (Docker ID: {container_id}) démarré par l'utilisateur (ID: {user_id}).")
        return jsonify({"message": "Conteneur démarré avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur lors du démarrage du conteneur {container_id} pour l'utilisateur {user_id}: {e}", exc_info=True)
        return jsonify({"message": f"Erreur interne du serveur: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_id):
    user_id = get_jwt_identity()
    container = Container.query.filter_by(docker_container_id=container_id, user_id=int(user_id)).first()
    if not container:
        logger.warning(f"Tentative d'arrêt de conteneur non autorisé ou inexistant: Docker ID={container_id}, UserID={user_id}")
        return jsonify({"message": "Conteneur non trouvé ou non autorisé"}), 404
    if not current_app.docker_service or not current_app.docker_service.client:
        logger.error("DockerService non initialisé ou client Docker non disponible.")
        return jsonify({"message": "Service Docker non disponible"}), 500
    try:
        current_app.docker_service.stop_container(container_id)
        container.status = 'exited'
        db.session.commit()
        if container.owner:
            logger.info(f"Conteneur '{container.name}' (Docker ID: {container_id}) arrêté par l'utilisateur {container.owner.username}.")
        else:
            logger.info(f"Conteneur '{container.name}' (Docker ID: {container_id}) arrêté par l'utilisateur (ID: {user_id}).")
        return jsonify({"message": "Conteneur arrêté avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur lors de l'arrêt du conteneur {container_id} pour l'utilisateur {user_id}: {e}", exc_info=True)
        return jsonify({"message": f"Erreur interne du serveur: {str(e)}"}), 500

@container_bp.route('/<string:container_id>/remove', methods=['DELETE'])
@jwt_required()
def remove_container(container_id):
    user_id = get_jwt_identity()

    try:
        # Find the container in the database.
        container = Container.query.filter_by(docker_container_id=container_id, user_id=int(user_id)).first()

        if not container:
            logger.warning(f"Tentative de suppression de conteneur non autorisé ou inexistant: Docker ID={container_id}, UserID={user_id}")
            return jsonify({"message": "Conteneur non trouvé ou non autorisé"}), 404

        # Log the container name and owner's name BEFORE deleting the object
        owner_username = container.owner.username if container.owner else f"ID: {user_id}"
        log_message = f"Conteneur '{container.name}' (Docker ID: {container_id}) supprimé par l'utilisateur {owner_username}."

        if not current_app.docker_service or not current_app.docker_service.client:
            logger.error("DockerService non initialisé ou client Docker non disponible.")
            # We can still delete from the database even if Docker is down.
            db.session.delete(container)
            db.session.commit()
            logger.info(f"DockerService non disponible. Entrée de base de données supprimée pour le conteneur {container_id}.")
            return jsonify({"message": "Service Docker non disponible. L'entrée du conteneur a été supprimée de la base de données."}), 200

        # Attempt to delete the container from the Docker daemon first
        try:
            current_app.docker_service.delete_container(container_id)
        except APIError as e:
            if 'not found' in str(e).lower():
                logger.warning(f"Conteneur {container_id} introuvable sur le daemon Docker, mais trouvé dans la DB. Suppression de la DB seule.")
            else:
                logger.error(f"Erreur lors de la suppression du conteneur Docker {container_id}: {e}")
                return jsonify({"message": f"Erreur interne du serveur: Échec de la suppression du conteneur Docker: {str(e)}"}), 500

        # If Docker removal was successful (or container was not found on Docker), delete from the database
        db.session.delete(container)
        db.session.commit()
        logger.info(log_message)
        return jsonify({"message": "Conteneur supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur inattendue lors de la suppression du conteneur {container_id}: {e}", exc_info=True)
        return jsonify({"message": f"Erreur interne du serveur: {str(e)}"}), 500
        
@container_bp.route('/list', methods=['GET'])
@jwt_required()
def list_containers():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    try:
        if not current_app.docker_service or not current_app.docker_service.client:
            return jsonify({"message": "Service Docker non disponible"}), 500

        db_containers = Container.query.filter_by(user_id=user.id).all()

        docker_containers = current_app.docker_service.list_all_containers()

        print(f"DEBUG: Conteneurs de la base de données: {[c.docker_container_id for c in db_containers]}")
        print(f"DEBUG: Conteneurs du daemon Docker: {[c.get('id') for c in docker_containers]}")

        response_data = []
        for db_container in db_containers:
            docker_info = next((c for c in docker_containers if c.get('id') == db_container.docker_container_id), None)
            status = docker_info.get('status', 'not found') if docker_info else 'not found'
            
            try:
                parsed_ports = json.loads(db_container.ports) if db_container.ports else []
            except (json.JSONDecodeError, TypeError):
                parsed_ports = []
            
            try:
                parsed_environment = json.loads(db_container.environment) if db_container.environment else {}
            except (json.JSONDecodeError, TypeError):
                parsed_environment = {}

            response_data.append({
                "id": db_container.id,
                "docker_id": db_container.docker_container_id,
                "name": db_container.name,
                "image": db_container.image,
                "status": status,
                "ports": parsed_ports,
                "environment": parsed_environment
            })

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des conteneurs pour l'utilisateur {user.username}: {e}", exc_info=True)
        return jsonify({"message": "Erreur interne du serveur lors de la récupération des conteneurs"}), 500