"""
Configuration générale du projet Amundi GEM Scraper
"""
import os
from pathlib import Path

# Chemins de base
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JSON_DIR = DATA_DIR / "json"

# Configuration des sources et leurs langues
SOURCES_CONFIG = {
    "afg": {
        "name": "AFG (France)",
        "language": "fr",
        "enabled": True
    },
    "afm": {
        "name": "AFM (Pays-Bas)",
        "language": "en",
        "enabled": True
    },
    "alfi": {
        "name": "ALFI (Luxembourg)",
        "language": "en",
        "enabled": True
    },
    "amf": {
        "name": "AMF (France)",
        "language": "fr",
        "enabled": True
    },
    "cbi": {
        "name": "CBI (Irlande)",
        "language": "en",
        "enabled": True
    },
    "cssf": {
        "name": "CSSF (Luxembourg)",
        "language": "fr",
        "enabled": True
    },
    "esma": {
        "name": "ESMA (Europe)",
        "language": "en",
        "enabled": True
    },
    "finma": {
        "name": "FINMA (Suisse)",
        "language": "en",
        "enabled": True
    }
}

# Configuration Selenium
SELENIUM_CONFIG = {
    "headless": True,
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Création automatique des dossiers
def ensure_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas."""
    DATA_DIR.mkdir(exist_ok=True)
    JSON_DIR.mkdir(exist_ok=True)

ensure_directories()