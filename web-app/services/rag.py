"""Services de recherche et de génération pour l'app web."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st
from sqlalchemy import text

from .clients import get_chroma, get_db_engine, get_embeddings_client, get_llm_client


def fetch_database_stats() -> tuple[int, dict[str, int]]:
    """Récupère les statistiques de la base (articles et sources)."""
    engine = get_db_engine()
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar_one()

        result = conn.execute(
            text(
                """
                SELECT source, COUNT(*) as count
                FROM articles
                GROUP BY source
                ORDER BY count DESC
                """
            )
        )
        by_source = {row[0]: row[1] for row in result}

    return total, by_source


def search_documents(query: str, n_results: int = 5, source_filter: Optional[str] = None) -> Dict[str, Any]:
    """Effectue une recherche vectorielle dans Chroma."""
    embeddings_client = get_embeddings_client()
    chroma = get_chroma()

    query_embedding = embeddings_client.embed_text(query)
    where_filter = {"source": source_filter} if source_filter else None

    return chroma.search(
        query_embedding=query_embedding,
        n_results=n_results,
        where=where_filter,
    )


def _build_context(results: Dict[str, Any]) -> tuple[str, List[dict[str, Any]]]:
    """Construit le contexte et la liste des sources pour le prompt."""
    context_parts: list[str] = []
    sources_info: list[dict[str, Any]] = []

    for i, (text_chunk, metadata, distance) in enumerate(
        zip(
            results["documents"][0][:3],
            results["metadatas"][0][:3],
            results["distances"][0][:3],
        ),
        1,
    ):
        score = (1 - distance) * 100
        if score <= 30:
            continue

        context_parts.append(
            f"""
[Document {i}]
Source: {metadata.get('source')}
Titre: {metadata.get('title')}
Date: {metadata.get('date', 'N/A')}
Contenu: {text_chunk[:1000]}
"""
        )
        sources_info.append(
            {
                "source": metadata.get("source"),
                "title": metadata.get("title"),
                "url": metadata.get("url"),
                "score": score,
            }
        )

    context = "\n\n".join(context_parts)
    return context, sources_info


def generate_answer(query: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """Génère une réponse en s'appuyant sur les résultats RAG."""
    if not results["ids"] or not results["ids"][0]:
        return {
            "answer": "❌ Je n'ai trouvé aucun document pertinent dans ma base de données pour répondre à cette question. Essayer de reformuler votre question ou de vérifier l'orthographe.",
            "sources_used": 0,
            "model": None,
        }

    context, sources_info = _build_context(results)
    if not context:
        return {
            "answer": "⚠️ J'ai trouvé des documents mais ils ne semblent pas assez pertinents pour répondre à votre question avec confiance. Pouvez-vous reformuler votre question de manière plus précise ?",
            "sources_used": 0,
            "model": None,
        }

    system_prompt = """Tu es un assistant expert en réglementation financière européenne.
Tu réponds aux questions en te basant UNIQUEMENT sur les documents fournis.

Règles importantes :
- Réponds en français de manière claire et structurée
- Cite précisément les sources (numéro du document)
- Si l'information n'est pas dans les documents, dis-le clairement
- Sois précis et factuel
- Utilise des bullet points si nécessaire
"""

    user_prompt = f"""Question : {query}

Documents de référence :
{context}

Réponds à la question en te basant sur ces documents. Cite les sources [Document X] dans ta réponse."""

    client = get_llm_client()
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=1000,
    )

    answer = response.choices[0].message.content
    return {
        "answer": answer,
        "sources_used": len(sources_info),
        "sources_info": sources_info,
        "model": "gpt-5-nano",
    }


@st.cache_data(show_spinner=False)
def get_sidebar_metrics():
    """Retourne les métriques affichées dans la sidebar."""
    total_articles, by_source = fetch_database_stats()
    chroma_docs = get_chroma().count_documents()
    return total_articles, by_source, chroma_docs
