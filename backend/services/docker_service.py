# backend/services/docker_service.py

import docker
from docker.errors import NotFound, APIError
from docker.models.containers import Container as DockerContainer
import logging
from typing import Optional, Dict, Any, Union

class DockerService:
    def __init__(self, app_logger: logging.Logger, docker_host_uri: Optional[str] = None):
        self.app_logger = app_logger
        self.client: Optional[docker.DockerClient] = None
        self.docker_host_uri = docker_host_uri
        self._initialize_client()

    def _initialize_client(self):
        try:
            if self.docker_host_uri:
                self.client = docker.DockerClient(base_url=self.docker_host_uri)
            else:
                self.client = docker.from_env()
            self.client.ping()
            self.app_logger.info("Docker client connected and daemon accessible!")
        except Exception as e:
            self.app_logger.error(f"Attempting to connect to Docker daemon via environment variables (docker.from_env()).")
            self.app_logger.error(f"Error connecting to Docker daemon: {e}")
            self.client = None

    def _check_client(self) -> bool:
        if not self.client:
            self.app_logger.error("Docker service not initialized or not connected.")
            return False
        try:
            self.client.ping()
            return True
        except Exception as e:
            self.app_logger.error(f"Connection to Docker daemon lost: {e}")
            self.client = None
            return False

    def _parse_ports_string(self, ports_str: Optional[str]) -> Optional[Dict[str, Optional[int]]]:
        """
        Parses a port string like '8080:80/tcp' or '5000' into a format compatible with docker-py.
        Returns a dictionary like {'80/tcp': 8080} or {'5000/tcp': None}.
        """
        if not ports_str:
            return None

        parsed_ports: Dict[str, Optional[int]] = {}
        # Handles multiple port mappings separated by commas
        for p_map in ports_str.split(','):
            p_map = p_map.strip()
            if not p_map:
                continue

            try:
                # Format: "HOST_PORT:CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT"
                if ':' in p_map:
                    host_part, container_part = p_map.split(':', 1)
                    host_port = int(host_part) # Converts host port to integer

                    if '/' in container_part:
                        container_port_str, protocol = container_part.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{container_part}/tcp" # Assume TCP if not specified

                    parsed_ports[container_port_key] = host_port # Maps container port to host port
                else:
                    # Format: "CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT"
                    if '/' in p_map:
                        container_port_str, protocol = p_map.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{p_map}/tcp" # Assume TCP if not specified

                    # When only the container port is specified, docker-py will assign a random host port
                    parsed_ports[container_port_key] = None # Docker will assign a random host port
            except ValueError:
                self.app_logger.error(f"Invalid port format encountered: {p_map}. Expected 'HOST_PORT:CONTAINER_PORT/PROTOCOL' or 'CONTAINER_PORT/PROTOCOL'.")
                raise ValueError(f"Invalid port format: {p_map}")
            except Exception as e:
                self.app_logger.error(f"Unexpected error when parsing port {p_map}: {e}")
                raise

        return parsed_ports if parsed_ports else None # Returns None if empty, or the dictionary

    def create_and_run_container(self, name: str, image: str, ports: Optional[str] = None, environment: Optional[Dict[str, str]] = None, network: Optional[str] = None, volumes: Optional[Dict[str, Dict[str, str]]] = None) -> Optional[DockerContainer]:
        if not self._check_client():
            self.app_logger.error("Docker service not available for container creation.")
            return None

        docker_ports_mapping = self._parse_ports_string(ports)

        restart_policy = {"Name": "unless-stopped"}

        try:
            container: DockerContainer = self.client.containers.run( # type: ignore [union-attr]
                image=image,
                name=name,
                detach=True,
                ports=docker_ports_mapping,
                environment=environment,
                network=network,
                volumes=volumes,
                restart_policy=restart_policy # type: ignore [arg-type]
            )
            self.app_logger.info(f"Container '{name}' created with ID: {container.id}")
            return container
        except APIError as e:
            self.app_logger.error(f"Docker API error during container creation: {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Unexpected error during container creation: {e}")
            raise

    def start_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Docker service unavailable.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.start()
            self.app_logger.info(f"Container '{container_id}' started.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for start operation.")
            raise
        except APIError as e:
            self.app_logger.error(f"Docker API error starting container '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Unexpected error starting container '{container_id}': {e}")
            raise

    def stop_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Docker service unavailable.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.stop()
            self.app_logger.info(f"Container '{container_id}' stopped.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for stop operation.")
            raise
        except APIError as e:
            self.app_logger.error(f"Docker API error stopping container '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Unexpected error stopping container '{container_id}': {e}")
            raise

    def remove_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Docker service unavailable.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.remove()
            self.app_logger.info(f"Container '{container_id}' removed.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for remove operation.")
            raise
        except APIError as e:
            self.app_logger.error(f"Docker API error removing container '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Unexpected error removing container '{container_id}': {e}")
            raise

    def get_container_logs(self, container_id: str) -> str:
        if not self._check_client():
            raise Exception("Docker service unavailable.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            logs = container.logs().decode('utf-8')
            return logs
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for logs operation.")
            raise
        except APIError as e:
            self.app_logger.error(f"Docker API error retrieving logs for container '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Unexpected error retrieving logs for container '{container_id}': {e}")
            raise

    # --- ADD THIS NEW METHOD ---
    def get_container_status(self, container_id: str) -> Optional[str]:
        """
        Retrieves the current status of a Docker container directly from the Docker daemon.
        Returns the status string (e.g., 'running', 'exited') or None if not found/error.
        """
        if not self._check_client():
            self.app_logger.error("Docker service unavailable to get container status.")
            return None
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            return container.status
        except NotFound:
            self.app_logger.warning(f"Container '{container_id}' not found for status check.")
            return None
        except APIError as e:
            self.app_logger.error(f"Docker API error getting status for container '{container_id}': {e}")
            return None
        except Exception as e:
            self.app_logger.error(f"Unexpected error getting status for container '{container_id}': {e}")
            return None
    # --- END NEW METHOD ---