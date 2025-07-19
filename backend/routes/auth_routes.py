# backend/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 
from marshmallow import ValidationError
from ..app import db 
from ..models import User
from ..schemas import user_register_schema, user_login_schema, user_schema
from sqlalchemy.exc import IntegrityError
import logging
from typing import Dict, Any, Optional

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    json_data: Optional[Dict[str, Any]] = request.get_json()
    if not json_data:
        logger.warning("Tentative d'enregistrement sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Validation des données d'entrée avec Marshmallow
        validated_data = user_register_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de l'enregistrement: {err.messages}")
        return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), 400

    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    try:
        # Vérifier si l'utilisateur ou l'email existe déjà (avant d'ajouter à la session pour une meilleure UX)
        if User.query.filter_by(username=username).first():
            logger.warning(f"Tentative d'enregistrement avec nom d'utilisateur existant: {username}")
            return jsonify({"msg": "Nom d'utilisateur déjà existant"}), 409
        if User.query.filter_by(email=email).first():
            logger.warning(f"Tentative d'enregistrement avec email existant: {email}")
            return jsonify({"msg": "Email déjà existant"}), 409

        logger.info(f"Création d'un nouvel utilisateur: {username} avec email: {email}.")
        new_user = User(username=username, email=email)
        new_user.set_password(password) # Cette méthode devrait gérer le hachage وتحديث created_at/updated_at
        
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"Utilisateur {username} enregistré avec succès dans la base de données. ID: {new_user.id}")

        return jsonify({"msg": "Utilisateur enregistré avec succès", "user": user_schema.dump(new_user)}), 201

    except IntegrityError:
        db.session.rollback()
        # Cette erreur peut se produire si une contrainte unique est violée (race condition)
        logger.error(f"Erreur d'intégrité (doublon) lors de l'enregistrement de l'utilisateur {username} ou {email}.")
        return jsonify({"msg": "Nom d'utilisateur ou email déjà existant"}), 409
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur inattendue lors de l'enregistrement: {e}", exc_info=True)
        return jsonify({"msg": "Erreur interne du serveur"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
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

    user = User.query.filter_by(username=username).first()

    # Utilise la méthode check_password() du modèle User
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id)) # Assurez-vous que l'identité est une chaîne
        logger.info(f"Utilisateur {username} connecté avec succès.")
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username} (informations d'identification invalides).")
        return jsonify({"msg": "Nom d'utilisateur ou mot de passe invalide"}), 401

# --- NOUVEAU: Route protégée pour le profil utilisateur ---
@auth_bp.route('/profile', methods=['GET'])
@jwt_required() 
def profile():
    current_user_id = get_jwt_identity() # Récupère l'identité (ID utilisateur) du jeton JWT
    user = User.query.get(current_user_id) # Recherche l'utilisateur par son ID

    if not user:
        logger.error(f"Utilisateur (ID: {current_user_id}) non trouvé lors de l'accès au profil, malgré un jeton valide.")
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    logger.info(f"Accès au profil de l'utilisateur: {user.username} (ID: {user.id}).")
    # Sérialise les données de l'utilisateur à renvoyer, excluant les informations sensibles comme le hachage du mot de passe
    return jsonify(user_schema.dump(user)), 200