"""
Configuration de la base de données MySQL
Gère la connexion et les paramètres DB
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ⚙️ Configuration Database
# TODO: Migrer vers des variables d'environnement (.env)
DB_CONFIG = {
    "user": os.getenv("DB_USER", "dhippo_user"),
    "password": os.getenv("DB_PASSWORD", "dhippo_password"),
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "3307"),
    "database": os.getenv("DB_NAME", "amundi")
}

# Construction de l'URL de connexion
def get_database_url():
    """Construit l'URL de connexion MySQL."""
    return (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

# Engine SQLAlchemy global
_engine = None
_SessionLocal = None

def get_engine():
    """Retourne l'engine SQLAlchemy (singleton)."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,  # Vérifie la connexion avant utilisation
            pool_recycle=3600    # Recycle les connexions après 1h
        )
    return _engine

def get_session():
    """Retourne une nouvelle session SQLAlchemy."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal()

# Test de connexion
def test_connection():
    """Teste la connexion à la base de données."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion DB : {e}")
        return False