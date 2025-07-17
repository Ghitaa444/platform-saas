# backend/config.py

import os
from dotenv import load_dotenv
from datetime import timedelta # Importation nécessaire pour timedelta

load_dotenv() # Charge les variables d'environnement depuis .env

class Config:
    """Configuration de base pour l'application Flask."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'une_cle_secrete_tres_longue_et_aleatoire_pour_le_dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = False

    # Configuration de la base de données
    # Utilise os.path.join pour construire un chemin absolu et robuste
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', 'site.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Désactiver pour améliorer la performance

    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key-NON-POUR-PROD') # Clé secrète JWT
    # Assurez-vous que JWT_ACCESS_TOKEN_EXPIRES est bien un int ou convertissez-le en timedelta
    # Pour être compatible avec Flask-JWT-Extended
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))) # Durée de validité du token

    # URI du démon Docker. Laisser None pour détection automatique (Docker Desktop).
    DOCKER_HOST_URI = os.getenv('DOCKER_HOST_URI')

class DevelopmentConfig(Config):
    """Configuration spécifique au développement."""
    DEBUG = True
    # Pas de modification sur DOCKER_HOST_URI, il peut être défini dans .env pour le développement

class TestingConfig(Config):
    """Configuration spécifique aux tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Base de données en mémoire pour les tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60) # Tokens JWT courts pour les tests
    # Désactiver la connexion Docker pour les tests unitaires afin d'éviter les dépendances externes
    DOCKER_HOST_URI = None # <-- AJOUTÉ / MODIFIÉ : Désactive la connexion Docker pour les tests

class ProductionConfig(Config):
    """Configuration spécifique à la production."""
    DEBUG = False
    TESTING = False
    # Assurer que les clés critiques sont définies via les variables d'environnement système en production
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or Config.JWT_SECRET_KEY
    DOCKER_HOST_URI = os.environ.get('DOCKER_HOST_URI') # Laisse la variable d'env pour la prod
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL doit être défini en production.")

# Mappage des noms de configuration aux classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}