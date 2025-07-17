# Dockerfile (à la racine du projet SaaS)
FROM python:3.11-slim-buster

# Définit le répertoire de travail DANS le conteneur.
# Toutes les commandes suivantes (COPY, RUN, CMD) seront exécutées par rapport à /app.
WORKDIR /app

# Copie le fichier requirements.txt et installe les dépendances.
# TRÈS IMPORTANT : Assurez-vous que le chemin ci-dessous correspond à l'emplacement réel de votre requirements.txt.
# Si requirements.txt est à la racine de votre projet (à côté de ce Dockerfile) :
COPY requirements.txt .
# Si requirements.txt est dans votre dossier 'backend' :
# COPY backend/requirements.txt ./backend/


# Exécute l'installation des dépendances.
# Si requirements.txt était à la racine:
RUN pip install --no-cache-dir -r requirements.txt
# Si requirements.txt était dans backend/:
# RUN pip install --no-cache-dir -r ./backend/requirements.txt


# Copie tout le dossier 'backend' (contenant votre code Flask) dans le conteneur.
# Le dossier 'backend' de votre hôte sera copié dans '/app/backend' dans le conteneur.
COPY backend/ ./backend/

# Commande pour démarrer l'application Flask avec Gunicorn.
# Le chemin 'backend.app:app' suppose que votre objet Flask est nommé 'app'
# dans le fichier 'app.py' situé dans le dossier 'backend' du conteneur.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]