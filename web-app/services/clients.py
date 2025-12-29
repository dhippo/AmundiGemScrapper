"""Clients et ressources partagés pour l'application web."""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from config.database import get_engine
from src.embeddings import OpenAIEmbeddings
from src.vectorstore import ChromaManager

# Charger les variables d'environnement dès le démarrage
load_dotenv()


@st.cache_resource(show_spinner=False)
def get_chroma() -> ChromaManager:
    """Initialise et met en cache le gestionnaire ChromaDB."""
    return ChromaManager()


@st.cache_resource(show_spinner=False)
def get_embeddings_client() -> OpenAIEmbeddings:
    """Initialise et met en cache le client d'embedddings OpenAI."""
    return OpenAIEmbeddings()


@st.cache_resource(show_spinner=False)
def get_llm_client() -> OpenAI:
    """Initialise et met en cache le client OpenAI pour le LLM."""
    return OpenAI()


@st.cache_resource(show_spinner=False)
def get_db_engine():
    """Initialise et met en cache le moteur SQLAlchemy."""
    return get_engine()
