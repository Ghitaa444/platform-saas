# backend/config.py
import os
from datetime import timedelta 

class Config:
    """Configuration de base pour l'application Flask."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'une_cle_secrete_tres_longue_et_aleatoire_pour_le_dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Désactiver pour améliorer la performance

    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key-NON-POUR-PROD') # Clé secrète JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))) # Durée de validité du token

    DOCKER_HOST_URI = os.getenv('DOCKER_HOST_URI')

class DevelopmentConfig(Config):
    """Configuration spécifique au développement."""
    DEBUG = True

class TestingConfig(Config):
    """Configuration spécifique aux tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Base de données en mémoire pour les tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60) # Tokens JWT courts pour les tests
    DOCKER_HOST_URI = None 

class ProductionConfig(Config):
    """Configuration spécifique à la production."""
    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__() 
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        self.DOCKER_HOST_URI = os.environ.get('DOCKER_HOST_URI')

        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environment variables.")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production environment variables.")
        if not self.SQLALCHEMY_DATABASE_URI:
        
            raise ValueError("DATABASE_URL must be set in production environment variables.")

# Mappage des noms de configuration aux classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}