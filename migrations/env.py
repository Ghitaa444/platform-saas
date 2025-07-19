# C:\newlocations\platform_saas\migrations\env.py

import os
import sys
import logging
from logging.config import fileConfig

# --- Start of Added/Modified Lines ---

# Add the project root to the sys.path so alembic.ini can be found
# Assuming env.py is in 'migrations/' and alembic.ini is in the parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set the FLASK_APP environment variable. This is crucial for Flask-Migrate
# to find your Flask application instance correctly.
# Assuming your Flask app instance is created in 'backend/app.py' and named 'app'
os.environ['FLASK_APP'] = 'backend.app'

# --- End of Added/Modified Lines ---


from flask import current_app
from alembic import context
from sqlalchemy import create_engine

from backend.database import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Start of CORRECTED fileConfig line ---
# Explicitly construct the path to alembic.ini in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
alembic_ini_path = os.path.join(project_root, 'alembic.ini')
fileConfig(alembic_ini_path) # Use the explicitly constructed path
# --- End of CORRECTED fileConfig line ---

logger = logging.getLogger('alembic.env')


# This is the target metadata for Alembic to detect changes.
# It should point to the db.Model.metadata that Flask-SQLAlchemy uses.
target_metadata = db.metadata

# If you have multiple metadata objects (e.g., for different database schemas),
# you might need a more complex get_metadata function.
# For a standard Flask-SQLAlchemy setup, db.metadata is usually sufficient.
def get_metadata():
    if hasattr(db, 'metadatas'):
        # For Flask-SQLAlchemy versions that use a collection of metadatas
        # if you have multiple binds/databases configured.
        return db.metadatas[None] # 'None' typically refers to the default bind
    return db.metadata # For standard setups


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and a target metadata to produce the 'in memory'
    tokenization of the migration script.

    Does not actually connect to the database.
    """
    with current_app.app_context():
        url = current_app.config['SQLALCHEMY_DATABASE_URI']
        context.configure(
            url=url, target_metadata=get_metadata(), literal_binds=True
        )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    with current_app.app_context():
        # Retrieve the database URI from your Flask app's configuration
        SQLALCHEMY_DATABASE_URI = current_app.config['SQLALCHEMY_DATABASE_URI']
        connectable = create_engine(SQLALCHEMY_DATABASE_URI)
        print(f"DEBUG: SQLALCHEMY_DATABASE_URI from app config: {SQLALCHEMY_DATABASE_URI}") # Keep for debugging if needed

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            dialect_name='postgresql', # Explicitly set dialect if auto-detection fails
            # include_object=include_object, # uncomment if you need to filter objects
            # process_revision_directives=process_revision_directives, # uncomment if you have custom revision directives
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()