import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context
import os
import sys

# Ajouter le chemin de l'application
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models import db
from app import create_app
from config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Créer l'application Flask pour avoir le contexte
app = create_app(Config)
app.app_context().push()

def get_engine():
    return db.engine

def get_engine_url():
    return str(get_engine().url)

config.set_main_option('sqlalchemy.url', get_engine_url())
target_metadata = db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()