# backend/routes/container_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.schemas import container_create_schema, container_schema
from backend.models import Container, User
from backend.database import db
import logging
# --- NEW IMPORTS ---
from docker.errors import NotFound, APIError
# --- END NEW IMPORTS ---

container_bp = Blueprint('containers', __name__, url_prefix='/containers')
logger = logging.getLogger(__name__)

@container_bp.route('/', methods=['POST'])
@jwt_required()
def create_container():
    logger.info("Received request to create a container.")

    try:
        container_data = container_create_schema.load(request.json)
        logger.debug(f"Container data loaded: {container_data}")
    except Exception as e:
        logger.error(f"Validation error for container creation: {e.messages}", exc_info=True)
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    # Ensure Docker service is initialized before trying to use its client
    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503 # Use 503 Service Unavailable

    try:
        name = container_data['name']
        image = container_data['image']
        ports_str = container_data.get('ports')

        logger.info(f"Attempting to create Docker container: Name={name}, Image={image}, Ports={ports_str}")
        docker_container = current_app.docker_service.create_and_run_container( # Use new method name
            name=name,
            image=image,
            ports=ports_str # Pass the raw string to the new parser
        )

        if not docker_container:
            logger.error(f"Failed to create Docker container for image {image}.")
            return jsonify({"error": "Failed to create Docker container"}), 500

        logger.info(f"Docker container created successfully: {docker_container.id}")
        new_container = Container(
            user_id=current_user_id,
            name=name,
            image=image,
            docker_container_id=docker_container.id,
            status=docker_container.status, # 'running' or similar
            ports=ports_str # Store the raw string back
        )
        db.session.add(new_container)
        db.session.commit()
        logger.info(f"Container saved to DB: {new_container.id}")

        return jsonify({
            "message": "Container created and started successfully",
            "container": container_schema.dump(new_container)
        }), 201

    except ValueError as ve: # Catch parsing errors from _parse_ports_string
        db.session.rollback()
        logger.error(f"Port parsing error during container creation: {ve}", exc_info=True)
        return jsonify({"error": str(ve)}), 400
    except APIError as e:
        db.session.rollback()
        logger.error(f"Docker API error during container creation: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        db.session.rollback()
        logger.critical(f"An unexpected error occurred during container creation: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred during container creation"}), 500


@container_bp.route('/', methods=['GET'])
@jwt_required()
def list_containers():
    logger.info("Received request to list containers.")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    user_containers = Container.query.filter_by(user_id=current_user_id).all()
    logger.debug(f"Found {len(user_containers)} containers for user {current_user_id}.")

    
    return jsonify(container_schema.dump(user_containers, many=True)), 200

# --- REFURBISHED STOP ROUTE ---
@container_bp.route('/<int:container_db_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_db_id):
    logger.info(f"Received request to stop container with DB ID: {container_db_id}")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    container = Container.query.filter_by(id=container_db_id, user_id=current_user_id).first()

    if not container:
        logger.warning(f"Container with DB ID {container_db_id} not found or not owned by user {current_user_id}.")
        return jsonify({"error": "Container not found or not authorized"}), 404

    # Ensure Docker service is available before attempting Docker operations
    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503 # Service Unavailable

    try:
        logger.info(f"Attempting to stop Docker container '{container.name}' (Docker ID: {container.docker_container_id})")
        # Call the docker_service method. It will raise an exception on failure.
        current_app.docker_service.stop_container(container.docker_container_id)

        # After successful stop, get the *actual* updated status from Docker
        updated_docker_status = current_app.docker_service.get_container_status(container.docker_container_id)

        # Update DB status
        container.status = updated_docker_status if updated_docker_status else "unknown" # Fallback if status couldn't be retrieved
        db.session.commit()
        logger.info(f"Container {container.name} (DB ID: {container_db_id}) status updated to '{container.status}' in DB.")

        return jsonify({
            "message": "Container stopped successfully",
            "container": container_schema.dump(container)
        }), 200

    except NotFound:
        # This occurs if docker_service.stop_container or get_container_status raises NotFound
        db.session.rollback()
        logger.error(f"Container '{container.docker_container_id}' not found on Docker daemon for stopping or status check.")
        return jsonify({"error": "Container not found on Docker daemon"}), 404
    except APIError as e:
        # This catches any general Docker API errors
        db.session.rollback()
        logger.error(f"Docker API error stopping container {container.docker_container_id}: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        # Catch any other unexpected errors
        db.session.rollback()
        logger.critical(f"An unexpected error occurred while stopping container {container_db_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred"}), 500
# --- END REFURBISHED STOP ROUTE ---

@container_bp.route('/<int:container_db_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_db_id):
    logger.info(f"Received request to start container with DB ID: {container_db_id}")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    container = Container.query.filter_by(id=container_db_id, user_id=current_user_id).first()

    if not container:
        logger.warning(f"Container with DB ID {container_db_id} not found or not owned by user {current_user_id}.")
        return jsonify({"error": "Container not found or not authorized"}), 404

    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503

    try:
        logger.info(f"Attempting to start Docker container '{container.name}' (Docker ID: {container.docker_container_id})")
        current_app.docker_service.start_container(container.docker_container_id)

        # After successful start, get the actual updated status from Docker
        updated_docker_status = current_app.docker_service.get_container_status(container.docker_container_id)

        # Update DB status
        container.status = updated_docker_status if updated_docker_status else "unknown"
        db.session.commit()
        logger.info(f"Container {container.name} (DB ID: {container_db_id}) status updated to '{container.status}' in DB.")

        return jsonify({
            "message": "Container started successfully",
            "container": container_schema.dump(container)
        }), 200

    except NotFound:
        db.session.rollback()
        logger.error(f"Container '{container.docker_container_id}' not found on Docker daemon for starting.")
        return jsonify({"error": "Container not found on Docker daemon"}), 404
    except APIError as e:
        db.session.rollback()
        logger.error(f"Docker API error starting container {container.docker_container_id}: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        db.session.rollback()
        logger.critical(f"An unexpected error occurred while starting container {container_db_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred"}), 500
# --- END NEW ROUTE ---

@container_bp.route('/<int:container_db_id>/remove', methods=['DELETE']) # Using DELETE method for removal
@jwt_required()
def remove_container(container_db_id):
    logger.info(f"Received request to remove container with DB ID: {container_db_id}")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    container = Container.query.filter_by(id=container_db_id, user_id=current_user_id).first()

    if not container:
        logger.warning(f"Container with DB ID {container_db_id} not found or not owned by user {current_user_id}.")
        return jsonify({"error": "Container not found or not authorized"}), 404

    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503

    try:
        logger.info(f"Attempting to remove Docker container '{container.name}' (Docker ID: {container.docker_container_id})")
        # Call the docker_service method to remove the container from Docker
        current_app.docker_service.remove_container(container.docker_container_id)

        # If Docker removal is successful, delete the record from the database
        db.session.delete(container)
        db.session.commit()
        logger.info(f"Container {container.name} (DB ID: {container_db_id}) successfully removed from Docker and DB.")

        return jsonify({
            "message": "Container removed successfully",
            "container_id": container_db_id, # Only return the ID, as the object is deleted
            "docker_container_id": container.docker_container_id
        }), 200

    except NotFound:
        db.session.rollback() # Rollback if delete fails after Docker call
        logger.error(f"Container '{container.docker_container_id}' not found on Docker daemon for removal. DB record not deleted.")
        return jsonify({"error": "Container not found on Docker daemon"}), 404
    except APIError as e:
        db.session.rollback()
        logger.error(f"Docker API error removing container {container.docker_container_id}: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        db.session.rollback()
        logger.critical(f"An unexpected error occurred while removing container {container_db_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred"}), 500
# --- END NEW ROUTE ---
@container_bp.route('/<int:container_db_id>/logs', methods=['GET'])
@jwt_required()
def get_container_logs_route(container_db_id): # Renamed to avoid conflict if any
    logger.info(f"Received request to get logs for container with DB ID: {container_db_id}")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    container = Container.query.filter_by(id=container_db_id, user_id=current_user_id).first()

    if not container:
        logger.warning(f"Container with DB ID {container_db_id} not found or not owned by user {current_user_id}.")
        return jsonify({"error": "Container not found or not authorized"}), 404

    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503

    try:
        logger.info(f"Attempting to retrieve logs for Docker container '{container.name}' (Docker ID: {container.docker_container_id})")
        logs = current_app.docker_service.get_container_logs(container.docker_container_id)

        return jsonify({
            "container_id": container_db_id,
            "docker_container_id": container.docker_container_id,
            "logs": logs
        }), 200

    except NotFound:
        logger.error(f"Container '{container.docker_container_id}' not found on Docker daemon for logs retrieval.")
        return jsonify({"error": "Container not found on Docker daemon"}), 404
    except APIError as e:
        logger.error(f"Docker API error retrieving logs for container {container.docker_container_id}: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        logger.critical(f"An unexpected error occurred while retrieving logs for container {container_db_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred"}), 500
# --- END NEW ROUTE ---
@container_bp.route('/<int:container_db_id>', methods=['GET']) # Note: This is a GET request to the base ID endpoint
@jwt_required()
def get_container_details(container_db_id):
    logger.info(f"Received request to get details for container with DB ID: {container_db_id}")

    current_user_id = get_jwt_identity()
    logger.debug(f"Current user ID from JWT: {current_user_id}")

    container_db_record = Container.query.filter_by(id=container_db_id, user_id=current_user_id).first()

    if not container_db_record:
        logger.warning(f"Container with DB ID {container_db_id} not found or not owned by user {current_user_id}.")
        return jsonify({"error": "Container not found or not authorized"}), 404

    if not current_app.docker_service or not current_app.docker_service._check_client():
        logger.error("Docker service is not initialized or client is not available.")
        return jsonify({"error": "Docker service is not available"}), 503

    try:
        logger.info(f"Attempting to inspect Docker container '{container_db_record.name}' (Docker ID: {container_db_record.docker_container_id})")
        
        # Get the Docker container object directly
        docker_container = current_app.docker_service.client.containers.get(container_db_record.docker_container_id) # type: ignore [union-attr]

        # Refresh its attributes to get the latest state
        docker_container.reload()

        # Combine database info with selected Docker daemon info
        details = {
            "id": container_db_record.id,
            "name": container_db_record.name,
            "image": container_db_record.image,
            "docker_container_id": container_db_record.docker_container_id,
            "status": docker_container.status, # Live status from Docker
            "ports": container_db_record.ports, # From DB, as it's the requested mapping
            "created_at_db": container_db_record.created_at.isoformat(), # DB creation timestamp
            "updated_at_db": container_db_record.updated_at.isoformat(), # DB last update timestamp
            "user_id": container_db_record.user_id,
            "docker_info": { # More detailed info directly from Docker inspect
                "State": docker_container.attrs.get('State'),
                "NetworkSettings": docker_container.attrs.get('NetworkSettings'),
                "Config": docker_container.attrs.get('Config')
                # You can add more fields from docker_container.attrs as needed
            }
        }
        
        # Update DB record with live status just in case (optional, but good for consistency)
        if container_db_record.status != docker_container.status:
            container_db_record.status = docker_container.status
            db.session.commit()
            logger.info(f"Container {container_db_id} status updated to '{docker_container.status}' during details retrieval.")


        return jsonify(details), 200

    except NotFound:
        # If container not found on Docker daemon, maybe it was manually removed
        logger.error(f"Container '{container_db_record.docker_container_id}' not found on Docker daemon. Removing from DB.")
        db.session.delete(container_db_record)
        db.session.commit()
        return jsonify({"error": "Container found in DB but not on Docker daemon, record removed."}), 404
    except APIError as e:
        logger.error(f"Docker API error getting details for container {container_db_record.docker_container_id}: {e}", exc_info=True)
        return jsonify({"error": f"Docker API error: {e}"}), 500
    except Exception as e:
        logger.critical(f"An unexpected error occurred while getting details for container {container_db_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred"}), 500
# --- END NEW ROUTE ---