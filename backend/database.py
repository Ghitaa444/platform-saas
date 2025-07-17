# backend/database.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instanciate the SQLAlchemy and Migrate objects
# They will be initialized with the Flask app in app.py
db = SQLAlchemy()
migrate = Migrate()