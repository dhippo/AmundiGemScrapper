"""Interface web Streamlit pour le RAG Amundi avec génération LLM."""
from __future__ import annotations

import streamlit as st

from services.rag import generate_answer, get_sidebar_metrics, search_documents
from ui.components import (
    question_form,
    render_answer,
    render_documents,
    render_footer,
    render_instructions,
    render_sources,
    sidebar_metrics,
)
from ui.layout import configure_page, render_header

configure_page()
render_header()

# Récupérer les métriques pour la sidebar et le formulaire
with st.spinner("Chargement des métriques..."):
    total_articles, by_source, chroma_docs = get_sidebar_metrics()

sidebar_metrics(total_articles, by_source, chroma_docs)

query, n_results, show_sources, source_filter = question_form(by_source)

results = None
answer_data = None

if st.button("🤖 Obtenir une réponse", use_container_width=True, type="primary"):
    if not query:
        st.warning("⚠️ Veuillez entrer une question")
    else:
        with st.spinner("🔍 Recherche des documents pertinents..."):
            results = search_documents(query, n_results, source_filter)

        with st.spinner("💭 Génération de la réponse..."):
            answer_data = generate_answer(query, results)

        render_answer(answer_data)
        render_sources(answer_data, show_sources)
        render_documents(results, show_sources)

render_instructions(query)
render_footer()
