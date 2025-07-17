# platform_saas/tests/test_api.py

import pytest
import os
import sys

# Ajuste le PYTHONPATH pour que Python puisse trouver les modules dans le dossier 'backend'
# C'est crucial pour que les imports comme 'from backend.app import create_app' fonctionnent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db # Importe l'objet 'db' de SQLAlchemy

@pytest.fixture
def client():
    """
    Fixture Pytest qui crée une instance de l'application Flask pour les tests,
    initialise une base de données SQLite en mémoire, et fournit un client de test.
    La base de données est supprimée après chaque test.
    """
    # Crée une instance de l'application avec la configuration 'testing'
    app = create_app('testing')

    # Contexte de l'application pour interagir avec la base de données
    with app.app_context():
        # Crée toutes les tables de la base de données en mémoire
        # Ceci est essentiel pour que les modèles SQLAlchemy puissent fonctionner
        db.create_all()
        yield app.test_client() # Fournit le client de test Flask au test
        # Nettoyage après le test : supprime la session et toutes les tables
        db.session.remove()
        db.drop_all()

def test_home_route(client):
    """
    Teste que la route GET / de l'API retourne le message d'accueil attendu
    avec un code de statut 200 OK.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to Platform SaaS API! Server is running."}