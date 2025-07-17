# backend/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from backend.database import db
from backend.models import User
from backend.schemas import user_register_schema, user_login_schema, user_schema
from sqlalchemy.exc import IntegrityError
import logging
from typing import Dict, Any, Optional # Ajouté pour Pylance


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    json_data: Optional[Dict[str, Any]] = request.get_json() # Ajouté annotation de type pour Pylance
    if not json_data:
        logger.warning("Tentative d'enregistrement sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        assert json_data is not None # Affirmer que json_data n'est pas None pour Pylance
        validated_data = user_register_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de l'enregistrement: {err.messages}")
        return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), 400

    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    try:
        # Vérifier si l'utilisateur ou l'email existe déjà avant de créer l'objet User
        if User.query.filter_by(username=username).first():
            logger.warning(f"Tentative d'enregistrement avec nom d'utilisateur existant: {username}")
            return jsonify({"msg": "Nom d'utilisateur déjà existant"}), 409
        if User.query.filter_by(email=email).first():
            logger.warning(f"Tentative d'enregistrement avec email existant: {email}")
            return jsonify({"msg": "Email déjà existant"}), 409

        logger.info(f"Tentative de création de l'objet User pour {username}.")
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        logger.info(f"Objet User créé pour {username}. Password haché.")

        logger.info(f"Ajout de l'utilisateur {username} à la session DB.")
        db.session.add(new_user)
        
        # Test 1: Log l'ID avant commit (si l'ID est généré avant le commit)
        logger.info(f"ID de l'utilisateur avant commit (peut être None si généré par DB): {new_user.id}")

        logger.info(f"Tentative de commit de l'utilisateur {username} dans la DB.")
        db.session.commit()
        logger.info(f"Utilisateur {username} commité avec succès dans la DB. ID final: {new_user.id}")

        logger.info(f"Nouvel utilisateur enregistré avec succès: {username} ({email})")
        return jsonify({"msg": "Utilisateur enregistré avec succès", "user": user_schema.dump(new_user)}), 201

    except IntegrityError:
        db.session.rollback()
        logger.error(f"Erreur d'intégrité (doublon) lors de l'enregistrement de l'utilisateur {username} ou {email}.")
        return jsonify({"msg": "Nom d'utilisateur ou email déjà existant"}), 409
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur inattendue lors de l'enregistrement: {e}", exc_info=True)
        return jsonify({"msg": "Erreur interne du serveur"}), 500

# Le reste du fichier (fonction login) reste inchangé
@auth_bp.route('/login', methods=['POST'])
def login():
    # ... votre code login ...
    json_data = request.get_json()
    if not json_data:
        logger.warning("Tentative de connexion sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Valider et charger les données d'entrée avec le schéma de connexion
        validated_data = user_login_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de la connexion: {err.messages}")
        return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), 400

    username = validated_data['username']
    password = validated_data['password']

    user = User.query.filter_by(username=username).first() # Recherche l'utilisateur par son nom d'utilisateur

    if user and user.check_password(password):
        # Création d'un jeton d'accès JWT en cas de connexion réussie
        access_token = create_access_token(identity=str(user.id))
        logger.info(f"Utilisateur {username} connecté avec succès.")
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username} (informations d'identification invalides).")
        return jsonify({"msg": "Nom d'utilisateur ou mot de passe invalide"}), 401