"""Configuration et éléments visuels communs."""
from __future__ import annotations

import streamlit as st


def configure_page() -> None:
    """Définit les paramètres généraux et le style global."""
    st.set_page_config(
        page_title="Amundi RAG | Veille Réglementaire",
        page_icon="🔍",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #0066cc;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .result-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #0066cc;
            margin-bottom: 1rem;
        }
        .answer-box {
            background-color: #e8f5e9;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #4caf50;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Affiche le titre et l'accroche principale."""
    st.title("🔍 Amundi GEM | Assistant Réglementaire")
    st.markdown("💬 *Posez vos questions, je réponds en me basant sur les documents officiels*")
    st.markdown("---")
