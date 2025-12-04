import docker
from docker.errors import NotFound, APIError, DockerException
from docker.models.containers import Container as DockerContainer
import logging
from typing import Optional, Dict, Any, Union, List


class DockerServiceException(Exception):
    """Custom exception for Docker service errors."""
    pass


class DockerService:
    """Service to interact with Docker daemon safely and efficiently."""

    def __init__(self, app_logger: logging.Logger, docker_host_uri: Optional[str] = None):
        self.app_logger = app_logger
        self.client: Optional[docker.DockerClient] = None
        self.docker_host_uri = docker_host_uri
        self._initialize_client()

    # ---------------------- 🔧 Internal setup ---------------------- #
    def _initialize_client(self):
        """Initialize Docker client and test connection."""
        try:
            if self.docker_host_uri:
                self.client = docker.DockerClient(base_url=self.docker_host_uri)
            else:
                self.client = docker.from_env()
            self.client.ping()
            self.app_logger.info("🐳 Docker client connected successfully.")
        except DockerException as e:
            self.app_logger.error(f"❌ Docker daemon unreachable: {e}", exc_info=True)
            self.client = None

    def _check_client(self) -> bool:
        """Ensure Docker client is alive and reinitialize if needed."""
        if not self.client:
            self._initialize_client()
            if not self.client:
                return False
        try:
            self.client.ping()
            return True
        except DockerException:
            self.client = None
            return False

    # ---------------------- 🧩 Utility ---------------------- #
    def _parse_ports_string(self, ports_str: Optional[str]) -> Optional[Dict[str, Optional[int]]]:
        """
        Parses ports string like '8080:80,443:443' into dict usable by docker-py.
        Returns None when input is falsy.
        """
        if not ports_str:
            return None
        parsed_ports: Dict[str, Optional[int]] = {}
        for p_map in ports_str.split(','):
            p_map = p_map.strip()
            if not p_map:
                continue
            try:
                if ':' in p_map:
                    host_part, container_part = p_map.split(':', 1)
                    host_port = int(host_part)
                    if '/' in container_part:
                        container_port_str, protocol = container_part.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{container_part}/tcp"
                    parsed_ports[container_port_key] = host_port
                else:
                    container_port_key = p_map if '/' in p_map else f"{p_map}/tcp"
                    parsed_ports[container_port_key] = None
            except Exception as e:
                raise DockerServiceException(f"Invalid port format: {p_map} ({e})")
        return parsed_ports or None

    # ---------------------- 🚀 Container Management ---------------------- #
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
        """Create and start a new Docker container."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")

        try:
            container = self.client.containers.create(
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
            self.app_logger.info(f"✅ Container '{name}' started successfully.")
            return container
        except NotFound:
            self.app_logger.warning(f"⚠️ Image '{image}' not found. Pulling...")
            self.client.images.pull(image)
            return self.create_container(name, image, ports, environment, network, volumes, cpu_shares, memory, command)
        except APIError as e:
            raise DockerServiceException(f"Docker API error during container creation: {e}")
        except Exception as e:
            raise DockerServiceException(f"Unexpected error creating container: {e}")

    def start_container(self, container_id: str):
        """Start a stopped container."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            c = self.client.containers.get(container_id)
            c.start()
            self.app_logger.info(f"▶️ Container '{c.name}' started.")
        except Exception as e:
            raise DockerServiceException(f"Error starting container: {e}")

    def stop_container(self, container_id: str):
        """Stop a running container."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            c = self.client.containers.get(container_id)
            c.stop()
            self.app_logger.info(f"⏸️ Container '{c.name}' stopped.")
        except Exception as e:
            raise DockerServiceException(f"Error stopping container: {e}")

    def delete_container(self, container_id: str):
        """Force remove a container."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            c = self.client.containers.get(container_id)
            c.remove(force=True)
            self.app_logger.info(f"🗑️ Container '{c.name}' deleted.")
        except Exception as e:
            raise DockerServiceException(f"Error deleting container: {e}")

    def get_container_logs(self, container_id: str) -> str:
        """Retrieve container logs."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            c = self.client.containers.get(container_id)
            logs = c.logs().decode('utf-8')
            self.app_logger.debug(f"📜 Logs for {c.name} fetched.")
            return logs
        except Exception as e:
            raise DockerServiceException(f"Error getting logs: {e}")

    def get_container_status(self, container_id: str) -> Optional[str]:
        """Return container running status."""
        if not self._check_client():
            return None
        try:
            return self.client.containers.get(container_id).status
        except NotFound:
            return "not_found"
        except Exception:
            return None

    def get_container_details(self, container_id: str) -> Dict[str, Any]:
        """Get detailed info for one container."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            c = self.client.containers.get(container_id)
            info = c.attrs
            ports = info.get("NetworkSettings", {}).get("Ports", {})
            networks = info.get("NetworkSettings", {}).get("Networks", {})
            return {
                "id": c.id,
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else "N/A",
                "status": c.status,
                "ports": ports,
                "networks": list(networks.keys()),
                "created": info.get("Created", "N/A")
            }
        except Exception as e:
            raise DockerServiceException(f"Error getting container details: {e}")

    # ---------------------- 📋 Listing ---------------------- #
    def list_all_containers(self) -> List[Dict[str, Any]]:
        """Return minimal list of all containers."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")
        try:
            containers = self.client.containers.list(all=True)
            return [
                {
                    "Id": c.id,
                    "Name": c.name,
                    "Status": c.status,
                    "Image": c.image.tags[0] if c.image.tags else 'N/A'
                }
                for c in containers
            ]
        except Exception as e:
            raise DockerServiceException(f"Error listing containers: {e}")

    def list_containers(self, only_app_containers: bool = False) -> List[Dict[str, Any]]:
        """Return detailed list of containers for UI consumption."""
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")

        try:
            containers = self.client.containers.list(all=True)
            result = []
            for c in containers:
                info = c.attrs
                name = info.get("Name", "").lstrip("/")
                if only_app_containers and not name.startswith("saas_"):
                    continue

                ports = []
                net_ports = info.get("NetworkSettings", {}).get("Ports", {}) or {}
                for port, binds in net_ports.items():
                    if binds:
                        for b in binds:
                            ports.append({
                                "container_port": port,
                                "host_ip": b.get("HostIp", "0.0.0.0"),
                                "host_port": b.get("HostPort", "N/A")
                            })
                    else:
                        ports.append({
                            "container_port": port,
                            "host_ip": None,
                            "host_port": None
                        })

                result.append({
                    "id": c.short_id,
                    "name": name,
                    "image": info.get("Config", {}).get("Image", ""),
                    "status": info.get("State", {}).get("Status", ""),
                    "created": info.get("Created", ""),
                    "ports": ports,
                })
            return result
        except Exception as e:
            raise DockerServiceException(f"Error listing containers: {e}")

    # ---------------------- 📊 Stats ---------------------- #
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Returns an instant metrics snapshot for a container:
         - cpu_percent (float)
         - memory_percent (float)
         - memory_usage (int bytes)
         - memory_limit (int bytes)
         - uptime (str human-friendly)
         - ports (dict)
         - status (str)
        """
        if not self._check_client():
            raise DockerServiceException("Docker unavailable")

        try:
            c = self.client.containers.get(container_id)
            stats = c.stats(stream=False)

            # --- CPU usage calculation
            cpu_stats = stats.get("cpu_stats", {}) or {}
            precpu_stats = stats.get("precpu_stats", {}) or {}
            cpu_delta = (
                cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            )
            system_delta = (
                cpu_stats.get("system_cpu_usage", 0)
                - precpu_stats.get("system_cpu_usage", 0)
            )
            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cores = len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [])) or 1
                cpu_percent = (cpu_delta / system_delta) * cores * 100.0

            # --- Memory usage
            mem_stats = stats.get("memory_stats", {}) or {}
            mem_usage = mem_stats.get("usage", 0)
            mem_limit = mem_stats.get("limit", 0)
            mem_percent = (mem_usage / mem_limit * 100.0) if mem_limit else 0.0

            # --- Uptime
            started_at = c.attrs.get("State", {}).get("StartedAt")
            uptime = "—"
            if started_at:
                from datetime import datetime, timezone
                try:
                    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    delta = now - started
                    days, seconds = delta.days, delta.seconds
                    hrs, mins = seconds // 3600, (seconds % 3600) // 60
                    if days > 0:
                        uptime = f"{days}d {hrs}h"
                    elif hrs > 0:
                        uptime = f"{hrs}h {mins}m"
                    else:
                        uptime = f"{mins}m"
                except Exception:
                    uptime = "—"

            # --- Ports
            ports = c.attrs.get("NetworkSettings", {}).get("Ports", {}) or {}

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(mem_percent, 2),
                "memory_usage": mem_usage,
                "memory_limit": mem_limit,
                "uptime": uptime,
                "ports": ports,
                "status": c.status
            }

        except NotFound:
            raise DockerServiceException(f"Container '{container_id}' not found")
        except APIError as e:
            raise DockerServiceException(f"Docker API error: {e}")
        except Exception as e:
            raise DockerServiceException(f"Unable to get stats: {e}")
