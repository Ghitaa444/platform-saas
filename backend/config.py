import os
from datetime import timedelta
from dotenv import load_dotenv
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Construct the path to the .env file, assuming it's one directory up from 'backend'
dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

class Config:
    """Classe de configuration de base pour l'application Flask."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'une_cle_secrete_tres_longue_et_aleatoire_pour_le_dev')
    # Active ou désactive le mode débogage de Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = False

    # URI de la base de données SQLAlchemy (récupérée des variables d'environnement)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour les jetons JWT 
    # CHANGED: Now loading JWT_SECRET_KEY from environment variable
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_default_jwt_secret_key_if_env_not_set') 
    # Durée de validité d'un jeton d'accès JWT 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    DOCKER_HOST_URI = os.getenv('DOCKER_HOST_URI')

    FRONTEND_RESET_PASSWORD_URL = os.getenv('FRONTEND_RESET_PASSWORD_URL', 'http://localhost:3000/reset-password')

    # Paramètres de connexion au serveur de messagerie SMTP pour l'envoi d'e-mails
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587)) # Port standard pour TLS (ou 465 pour SSL)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't') # Active le chiffrement TLS
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't') # Active le chiffrement SSL (choisir TLS ou SSL, pas les deux)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@yourdomain.com') # Adresse e-mail de l'expéditeur par défaut
    # --- Fin des configurations liées à la messagerie ---

class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    # L'URL du frontend peut pointer vers localhost en développement
    FRONTEND_RESET_PASSWORD_URL = os.getenv('FRONTEND_RESET_PASSWORD_URL', 'http://localhost:3000/reset-password')

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Base de données en mémoire pour les tests unitaires
    # It's good to explicitly define JWT_SECRET_KEY for testing if it needs to be different
    JWT_SECRET_KEY = os.getenv('TEST_JWT_SECRET_KEY', 'your_test_secret_key_for_jwt') # Use a specific key for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60) # Jetons JWT de courte durée pour les tests
    DOCKER_HOST_URI = None 
    # Désactivation de l'envoi réel d'e-mails en mode test
    MAIL_SERVER = None
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'test@example.com'

class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__()
        # Ensure these are loaded from environment variables in production
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') # Now correctly loading from env in production
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        self.DOCKER_HOST_URI = os.environ.get('DOCKER_HOST_URI')

        # Récupération des variables spécifiques à la réinitialisation et aux e-mails en production
        self.FRONTEND_RESET_PASSWORD_URL = os.environ.get('FRONTEND_RESET_PASSWORD_URL')
        self.MAIL_SERVER = os.environ.get('MAIL_SERVER')
        self.MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
        self.MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't')
        self.MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't')
        self.MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        self.MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        self.MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

        # Validation pour s'assurer que les variables critiques sont bien définies en production
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY doit être définie dans les variables d'environnement de production.")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY doit être définie dans les variables d'environnement de production.")
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("SQLALCHEMY_DATABASE_URI doit être définie dans les variables d'environnement de production.")
        if not self.DOCKER_HOST_URI:
            raise ValueError("DOCKER_HOST_URI doit être définie pour l'intégration Docker en production.")
        
        # Avertissement si les configurations d'e-mail ne sont pas complètes en production
        if not self.MAIL_SERVER or not self.MAIL_USERNAME or not self.MAIL_PASSWORD or not self.MAIL_DEFAULT_SENDER:
            logger.warning("Les identifiants d'envoi d'e-mails ne sont pas entièrement configurés en production. Les fonctionnalités d'e-mail pourraient ne pas fonctionner.")

# Mappage des noms de configuration aux classes correspondantes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}