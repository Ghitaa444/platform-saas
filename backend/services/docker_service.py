# backend/services/docker_service.py

import docker
from docker.errors import NotFound, APIError
from docker.models.containers import Container as DockerContainer # Pour le type hint
import logging
from typing import Optional, Dict, Any, Tuple # Ajout des imports de typage

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
            self.client.ping() # Vérifie la connexion au démon Docker
            self.app_logger.info("Client Docker connecté et démon accessible!")
        except Exception as e:
            self.app_logger.error(f"Tentative de connexion au démon Docker via les variables d'environnement (docker.from_env()).")
            self.app_logger.error(f"Erreur de connexion au démon Docker: {e}")
            self.client = None

    def _check_client(self) -> bool:
        if not self.client:
            self.app_logger.error("Service Docker non initialisé ou non connecté.")
            return False
        try:
            self.client.ping()
            return True
        except Exception as e:
            self.app_logger.error(f"Connexion au démon Docker perdue: {e}")
            self.client = None
            return False

    def _parse_ports_string(self, ports_str: Optional[str]) -> Dict[str, Tuple[str, int]] | Dict[str, int] | None:
        """
        Parse une chaîne de ports comme '8080:80/tcp' ou '5000' en un format compatible avec docker-py.
        Retourne un dictionnaire comme {'80/tcp': ('0.0.0.0', 8080)} ou {'5000/tcp': 5000}.
        """
        if not ports_str:
            return None

        parsed_ports: Dict[str, Any] = {}
        # Gère plusieurs mappages de ports séparés par des virgules
        for p_map in ports_str.split(','):
            p_map = p_map.strip()
            if not p_map:
                continue

            try:
                # Format: "HOST_PORT:CONTAINER_PORT/PROTOCOL" ou "CONTAINER_PORT/PROTOCOL" ou "CONTAINER_PORT"
                if ':' in p_map:
                    host_part, container_part = p_map.split(':', 1)
                    host_port = int(host_part) # Convertit le port hôte en entier
                    
                    if '/' in container_part:
                        container_port_str, protocol = container_part.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{container_part}/tcp" # Assumer TCP si non spécifié
                    
                    parsed_ports[container_port_key] = host_port # Map le port du conteneur au port de l'hôte
                else:
                    # Format: "CONTAINER_PORT/PROTOCOL" ou "CONTAINER_PORT"
                    if '/' in p_map:
                        container_port_str, protocol = p_map.split('/')
                        container_port_key = f"{container_port_str}/{protocol}"
                    else:
                        container_port_key = f"{p_map}/tcp" # Assumer TCP si non spécifié
                    
                    # Quand seul le port du conteneur est spécifié, docker-py assignera un port aléatoire sur l'hôte
                    # Ou si c'est pour une publication simple, on peut laisser le port tel quel si c'est un int
                    parsed_ports[container_port_key] = None # Docker assignera un port hôte aléatoire
            except ValueError:
                self.app_logger.error(f"Format de port invalide rencontré: {p_map}. Attendu 'HOST_PORT:CONTAINER_PORT/PROTOCOL' ou 'CONTAINER_PORT/PROTOCOL'.")
                raise ValueError(f"Format de port invalide: {p_map}")
            except Exception as e:
                self.app_logger.error(f"Erreur inattendue lors de l'analyse du port {p_map}: {e}")
                raise

        return parsed_ports if parsed_ports else None # Retourne None si vide, ou le dictionnaire

    def create_and_run_container(self, name: str, image: str, ports: Optional[str] = None, environment: Optional[Dict[str, str]] = None, network: Optional[str] = None, volumes: Optional[Dict[str, Dict[str, str]]] = None) -> Optional[str]:
        if not self._check_client():
            raise Exception("Service Docker non disponible.")

        docker_ports_mapping = self._parse_ports_string(ports)
        
        # Policy de redémarrage par défaut
        restart_policy = {"Name": "unless-stopped"}

        try:
            container: DockerContainer = self.client.containers.run( # type: ignore [union-attr]
                image=image,
                name=name,
                detach=True,
                ports=docker_ports_mapping, # type: ignore [arg-type] # Pylance peut se plaindre du type, mais c'est le format attendu
                environment=environment,
                network=network,
                volumes=volumes,
                restart_policy=restart_policy  #type: ignore [arg-type] # AJOUTÉ ICI : Ignore le problème de typage pour restart_policy
            )
            self.app_logger.info(f"Conteneur '{name}' créé avec l'ID: {container.id}")
            return container.id
        except APIError as e:
            self.app_logger.error(f"Erreur API Docker lors de la création du conteneur: {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Erreur inattendue lors de la création du conteneur: {e}")
            raise

    def start_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Service Docker non disponible.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.start()
            self.app_logger.info(f"Conteneur '{container_id}' démarré.")
        except NotFound:
            self.app_logger.error(f"Conteneur '{container_id}' non trouvé pour l'opération de démarrage.")
            raise
        except APIError as e:
            self.app_logger.error(f"Erreur API Docker lors du démarrage du conteneur '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Erreur inattendue lors du démarrage du conteneur '{container_id}': {e}")
            raise

    def stop_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Service Docker non disponible.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.stop()
            self.app_logger.info(f"Conteneur '{container_id}' arrêté.")
        except NotFound:
            self.app_logger.error(f"Conteneur '{container_id}' non trouvé pour l'opération d'arrêt.")
            raise
        except APIError as e:
            self.app_logger.error(f"Erreur API Docker lors de l'arrêt du conteneur '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Erreur inattendue lors de l'arrêt du conteneur '{container_id}': {e}")
            raise

    def remove_container(self, container_id: str):
        if not self._check_client():
            raise Exception("Service Docker non disponible.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            container.remove()
            self.app_logger.info(f"Conteneur '{container_id}' supprimé.")
        except NotFound:
            self.app_logger.error(f"Conteneur '{container_id}' non trouvé pour l'opération de suppression.")
            raise
        except APIError as e:
            self.app_logger.error(f"Erreur API Docker lors de la suppression du conteneur '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Erreur inattendue lors de la suppression du conteneur '{container_id}': {e}")
            raise

    def get_container_logs(self, container_id: str) -> str:
        if not self._check_client():
            raise Exception("Service Docker non disponible.")
        try:
            container = self.client.containers.get(container_id) # type: ignore [union-attr]
            logs = container.logs().decode('utf-8')
            return logs
        except NotFound:
            self.app_logger.error(f"Conteneur '{container_id}' non trouvé pour l'opération de logs.")
            raise
        except APIError as e:
            self.app_logger.error(f"Erreur API Docker lors de la récupération des logs du conteneur '{container_id}': {e}")
            raise
        except Exception as e:
            self.app_logger.error(f"Erreur inattendue lors de la récupération des logs du conteneur '{container_id}': {e}")
            raise