"""Composants Streamlit pour l'interface web."""
from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def sidebar_metrics(total_articles: int, by_source: dict[str, int], chroma_docs: int) -> None:
    """Affiche les statistiques dans la barre latérale."""
    with st.sidebar:
        st.header("📊 Base de données")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Articles", total_articles)
        with col2:
            st.metric("Chunks", chroma_docs)

        st.markdown("---")
        st.subheader("📂 Par source")
        for source, count in by_source.items():
            st.text(f"{source}: {count}")

        st.markdown("---")
        st.info("🤖 **Modèle :** gpt-5-nano")
        st.caption("💡 Propulsé par OpenAI & ChromaDB")


def question_form(by_source: dict[str, int]) -> tuple[str, int, bool, str | None]:
    """Affiche le formulaire de question et retourne les paramètres choisis."""
    query = st.text_area(
        "Votre question",
        placeholder="Ex: Quelle est la position de l'AFG sur la facturation électronique ?",
        help="Posez une question en français ou en anglais",
        height=100,
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        sources = ["Toutes"] + list(by_source.keys())
        source_filter = st.selectbox("Filtrer par source", sources)
        if source_filter == "Toutes":
            source_filter = None

    with col2:
        n_results = st.selectbox("Documents", [3, 5, 10], index=1)

    with col3:
        show_sources = st.checkbox("Afficher sources", value=True)

    return query, n_results, show_sources, source_filter


def render_answer(answer_data: Dict[str, Any]) -> None:
    """Affiche la réponse générée et ses métriques."""
    with st.container():
        st.markdown("### 💡 Réponse")
        st.markdown(answer_data["answer"])

    if answer_data["model"]:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sources utilisées", answer_data["sources_used"])
        with col2:
            st.metric("Modèle", answer_data["model"])


def render_sources(answer_data: Dict[str, Any], show_sources: bool) -> None:
    """Affiche les sources utilisées et les documents détaillés."""
    if not show_sources or answer_data.get("sources_used", 0) <= 0:
        return

    st.markdown("---")
    st.subheader("📚 Sources consultées")

    for i, source_info in enumerate(answer_data["sources_info"], 1):
        with st.expander(
            f"📄 Source {i} - {source_info['source']} (Score: {source_info['score']:.1f}%)"
        ):
            st.markdown(f"**Titre :** {source_info['title']}")
            st.markdown(f"**URL :** [{source_info['url']}]({source_info['url']})")


def render_documents(results: Dict[str, Any], show_sources: bool) -> None:
    """Liste l'ensemble des documents trouvés."""
    if not show_sources or not results.get("ids") or not results["ids"][0]:
        return

    with st.expander("🔎 Voir tous les documents trouvés"):
        for i, (doc_id, text, metadata, distance) in enumerate(
            zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ),
            1,
        ):
            score = (1 - distance) * 100

            st.markdown(f"**Document {i}** - Score: {score:.1f}%")
            st.text(f"Source: {metadata.get('source')} | Date: {metadata.get('date', 'N/A')}")
            st.text(f"Titre: {metadata.get('title')[:80]}...")
            st.markdown(f"[Lien]({metadata.get('url')})")
            st.markdown("---")


def render_instructions(query: str) -> None:
    """Affiche les instructions d'utilisation initiales."""
    if query:
        return

    st.info("💡 **Comment utiliser cet assistant ?**")
    st.markdown(
        """
        1. **Posez votre question** dans le champ ci-dessus
        2. **Filtrez par source** si vous cherchez dans une autorité spécifique (optionnel)
        3. **Cliquez sur "Obtenir une réponse"** pour lancer la recherche
        4. **L'assistant génère une réponse** basée sur les documents officiels

        **Exemples de questions :**
        - "Quelle est la position de l'AFG sur la facturation électronique ?"
        - "Quelles sont les obligations de reporting EMIR 3.0 ?"
        - "Résume les principales mesures concernant les fonds d'investissement"
        - "Qu'est-ce que la grille d'impact pour la dette privée ?"
        """
    )


def render_footer() -> None:
    """Ajoute le pied de page de l'application."""
    st.markdown("---")
    st.caption("🏦 Amundi Asset Management | Assistant IA de Veille Réglementaire")
