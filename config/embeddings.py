"""
Configuration des embeddings OpenAI
"""
import os
from pathlib import Path

# ⚙️ Configuration OpenAI
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),  # À définir dans .env ou variable d'environnement
    "model": "text-embedding-3-small",
    "dimensions": 1536,  # Dimensions du modèle small
    "max_tokens": 8191,  # Limite du modèle
}

# ⚙️ Configuration Chunking
CHUNKING_CONFIG = {
    "chunk_size": 1000,      # Tokens par chunk
    "chunk_overlap": 200,    # Overlap entre chunks
    "min_chunk_size": 100,   # Taille minimale d'un chunk
}

# ⚙️ Configuration ChromaDB
CHROMA_CONFIG = {
    "persist_directory": Path(__file__).parent.parent / "data" / "chroma",
    "collection_name": "regulatory_articles",
    "distance_metric": "cosine",  # ou "l2", "ip"
}

# Création du dossier chroma
CHROMA_CONFIG["persist_directory"].mkdir(parents=True, exist_ok=True)


def validate_openai_key():
    """Vérifie que la clé API OpenAI est configurée."""
    if not OPENAI_CONFIG["api_key"]:
        raise ValueError(
            "⚠️  Clé API OpenAI manquante !\n"
            "Définis la variable d'environnement OPENAI_API_KEY :\n"
            "  export OPENAI_API_KEY='sk-...'"
        )
    return True