import docker
from docker.errors import NotFound, APIError
from docker.models.containers import Container as DockerContainer
import logging
from typing import Optional, Dict, Any, Union, List

# Defines a custom exception for Docker service errors.
class DockerServiceException(Exception):
    pass

class DockerService:
    """
    Service to interact with the Docker daemon.
    Manages connection, creation, starting, stopping, deletion, and retrieval of container information.
    """

    def __init__(self, app_logger: logging.Logger, docker_host_uri: Optional[str] = None):
        self.app_logger = app_logger
        self.client: Optional[docker.DockerClient] = None
        self.docker_host_uri = docker_host_uri
        self._initialize_client()

    def _initialize_client(self):
        """
        Initializes or re-initializes the Docker client.
        Tries to connect to the Docker daemon via the environment or a specified URI.
        """
        try:
            if self.docker_host_uri:
                self.client = docker.DockerClient(base_url=self.docker_host_uri)
            else:
                self.client = docker.from_env()
            self.client.ping()  # Verifies the connection to the daemon
            self.app_logger.info("Docker client connected and daemon is accessible!")
        except Exception as e:
            self.app_logger.error(f"Error connecting to Docker daemon: {e}", exc_info=True)
            self.client = None  # Ensures the client is None if the connection fails

    def _check_client(self) -> bool:
        """
        Checks if the Docker client is initialized and the connection to the daemon is active.
        Attempts to re-initialize the connection if the check fails.
        """
        if not self.client:
            self.app_logger.warning("Docker client is not initialized. Attempting to re-initialize.")
            self._initialize_client()  # Tries to initialize the client
            if not self.client:  # If initialization failed
                self.app_logger.error("Failed to re-initialize the Docker client.")
                return False

        try:
            self.client.ping()
            return True
        except Exception as e:
            self.app_logger.error(f"Connection to Docker daemon lost: {e}. Attempting to re-initialize.", exc_info=True)
            self.client = None  # Marks the client as not connected
            self._initialize_client()  # Tries to re-initialize the connection
            return self.client is not None  # Returns True if reconnection succeeded, False otherwise

    def _parse_ports_string(self, ports_str: Optional[str]) -> Optional[Dict[str, Optional[int]]]:
        """
        Parses a port string like '8080:80/tcp' or '5000' into a docker-py compatible format.
        Returns a dictionary like {'80/tcp': 8080} (host:container port mapping) or {'5000/tcp': None} (random host port).
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
                # Expected format: "HOST_PORT:CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT"
                if ':' in p_map:
                    host_part, container_part = p_map.split(':', 1)
                    host_port = int(host_part)  # Converts host port to integer

                    if '/' in container_part:
                        container_port_str, protocol = container_part.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{container_part}/tcp"  # Assumes TCP if not specified

                    parsed_ports[container_port_key] = host_port  # Maps container port to host port
                else:
                    # Format: "CONTAINER_PORT/PROTOCOL" or "CONTAINER_PORT"
                    if '/' in p_map:
                        container_port_str, protocol = p_map.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{p_map}/tcp"  # Assumes TCP if not specified

                    # When only the container port is specified, docker-py will assign a random host port
                    parsed_ports[container_port_key] = None  # Docker will assign a random host port
            except ValueError:
                self.app_logger.error(f"Invalid port format encountered: {p_map}. Expected 'HOST_PORT:CONTAINER_PORT/PROTOCOL' or 'CONTAINER_PORT/PROTOCOL'.")
                raise DockerServiceException(f"Invalid port format: {p_map}")
            except Exception as e:
                self.app_logger.error(f"Unexpected error parsing port {p_map}: {e}", exc_info=True)
                raise DockerServiceException(f"Unexpected error parsing ports: {e}")

        return parsed_ports if parsed_ports else None  # Returns None if empty, or the dictionary
    def create_container(
        self,
        name: str,
        image: str,
        ports: Optional[Dict[str, Union[int, tuple, None]]] = None,
        environment: Optional[Dict[str, str]] = None,
        network: Optional[str] = None,
        volumes: Optional[Union[List[str], Dict[str, Dict[str, str]]]] = None,
        cpu_shares: Optional[int] = None,
        memory: Optional[str] = None,
        command: Optional[Union[str, List[str]]] = None
    ) -> DockerContainer:
        """
        Creates and starts a container. Manages pulling the image if not found locally.
        Returns the created Docker container object. Raises DockerServiceException on failure.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot create the container.")

        try:
            self.app_logger.info(f"Creating and starting container '{name}' from image '{image}'...")
            
            # Use create() directly with all parameters
            container: DockerContainer = self.client.containers.create(
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                network=network,
                volumes=volumes,
                cpu_shares=cpu_shares,
                mem_limit=memory,
                command=command,
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            container.start()
            
            self.app_logger.info(f"Container '{name}' created and started successfully. ID: {container.id}")
            return container
            
        except NotFound:
            self.app_logger.warning(f"Image '{image}' not found locally. Attempting to pull...")
            try:
                self.client.images.pull(image)
                # Retry creation after the pull
                container: DockerContainer = self.client.containers.create(
                    image=image,
                    name=name,
                    ports=ports,
                    environment=environment,
                    network=network,
                    volumes=volumes,
                    cpu_shares=cpu_shares,
                    mem_limit=memory,
                    command=command,
                    detach=True,
                    restart_policy={"Name": "unless-stopped"}
                )
                container.start()
                self.app_logger.info(f"Image '{image}' pulled and container '{name}' created and started. ID: {container.id}")
                return container
            except Exception as pull_e:
                self.app_logger.error(f"Failed to pull image '{image}': {pull_e}")
                raise DockerServiceException(f"Failed to create container: image '{image}' not found and pull failed.") from pull_e

        except APIError as e:
            self.app_logger.error(f"Docker API error during container creation: {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during container creation: {e}")

        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during container creation: {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during container creation: {e}")

    def start_container(self, container_id: str):
        """
        Starts an existing Docker container. Raises DockerServiceException on failure.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot start the container.")
        try:
            container = self.client.containers.get(container_id)
            container.start()
            self.app_logger.info(f"Container '{container_id}' started.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for the start operation.")
            raise DockerServiceException(f"Container '{container_id}' not found.")
        except APIError as e:
            self.app_logger.error(f"Docker API error during container start for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during container start for '{container_id}': {e}")
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during container start for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during container start for '{container_id}': {e}")

    def stop_container(self, container_id: str):
        """
        Stops an existing Docker container. Raises DockerServiceException on failure.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot stop the container.")
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            self.app_logger.info(f"Container '{container_id}' stopped.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for the stop operation.")
            raise DockerServiceException(f"Container '{container_id}' not found.")
        except APIError as e:
            self.app_logger.error(f"Docker API error during container stop for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during container stop for '{container_id}': {e}")
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during container stop for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during container stop for '{container_id}': {e}")

    def delete_container(self, container_id: str):
        """
        Deletes an existing Docker container. Raises DockerServiceException on failure.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot delete the container.")
        try:
            container = self.client.containers.get(container_id)
            container.remove()
            self.app_logger.info(f"Container '{container_id}' deleted.")
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for the delete operation.")
            raise DockerServiceException(f"Container '{container_id}' not found.")
        except APIError as e:
            self.app_logger.error(f"Docker API error during container deletion for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during container deletion for '{container_id}': {e}")
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during container deletion for '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during container deletion for '{container_id}': {e}")

    def get_container_logs(self, container_id: str) -> str:
        """
        Retrieves the logs of a Docker container. Raises DockerServiceException on failure.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot retrieve logs.")
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs().decode('utf-8')
            return logs
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for the logs operation.")
            raise DockerServiceException(f"Container '{container_id}' not found.")
        except APIError as e:
            self.app_logger.error(f"Docker API error during log retrieval for container '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during log retrieval for container '{container_id}': {e}")
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during log retrieval for container '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during log retrieval for container '{container_id}': {e}")

    def get_container_status(self, container_id: str) -> Optional[str]:
        """
        Retrieves the current status of a Docker container directly from the Docker daemon.
        Returns the status string (e.g., 'running', 'exited', 'created') or None if not found/error.
        """
        if not self._check_client():
            self.app_logger.error("Docker service is unavailable to get container status.")
            return None
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except NotFound:
            self.app_logger.warning(f"Container '{container_id}' not found for status check.")
            return None
        except APIError as e:
            self.app_logger.error(f"Docker API error during status retrieval for container '{container_id}': {e}", exc_info=True)
            return None
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during status retrieval for container '{container_id}': {e}", exc_info=True)
            return None

    def get_container_details(self, container_id: str) -> Dict[str, Any]:
        """
        Retrieves all relevant details of a Docker container.
        Returns a dictionary with the details or raises DockerServiceException.
        """
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot retrieve container details.")
        try:
            container = self.client.containers.get(container_id)
            
            ip_address = 'N/A'
            if container.attrs and 'NetworkSettings' in container.attrs and 'Networks' in container.attrs['NetworkSettings']:
                for network_name, network_info in container.attrs['NetworkSettings']['Networks'].items():
                    if 'IPAddress' in network_info:
                        ip_address = network_info['IPAddress']
                        break

            ports_info = []
            if container.attrs and 'NetworkSettings' in container.attrs and 'Ports' in container.attrs['NetworkSettings']:
                for container_port, host_bindings in container.attrs['NetworkSettings']['Ports'].items():
                    if host_bindings:
                        for binding in host_bindings:
                            ports_info.append({
                                'container_port': container_port,
                                'host_ip': binding.get('HostIp', '0.0.0.0'),
                                'host_port': binding.get('HostPort', 'N/A')
                            })
                    else:
                        ports_info.append({'container_port': container_port, 'host_ip': 'N/A', 'host_port': 'N/A'})

            return {
                "id": container.id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else 'N/A',
                "status": container.status,
                "created": container.attrs.get('Created', 'N/A'),
                "ip_address": ip_address,
                "ports_info": ports_info,
                "labels": container.labels,
                "environment": container.attrs.get('Config', {}).get('Env', [])
            }
        except NotFound:
            self.app_logger.error(f"Container '{container_id}' not found for details retrieval.")
            raise DockerServiceException(f"Container '{container_id}' not found.")
        except APIError as e:
            self.app_logger.error(f"Docker API error during details retrieval for container '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"Docker API error during details retrieval for container '{container_id}': {e}")
        except Exception as e:
            self.app_logger.error(f"An unexpected error occurred during details retrieval for container '{container_id}': {e}", exc_info=True)
            raise DockerServiceException(f"An unexpected error occurred during details retrieval for container '{container_id}': {e}")

    def list_all_containers(self) -> List[Dict[str, Any]]:
        if not self._check_client():
            raise DockerServiceException("Docker service is unavailable. Cannot list containers.")
        try:
            containers = self.client.containers.list(all=True)
            return [{"Id": c.id, "Name": c.name, "Status": c.status, "Image": c.image.tags[0] if c.image.tags else 'N/A'} for c in containers]
        except Exception as e:
            self.app_logger.error(f"Error listing all Docker containers: {e}", exc_info=True)
            raise DockerServiceException(f"Error listing all Docker containers: {e}")