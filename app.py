"""
Interface web Streamlit pour le RAG Amundi avec génération LLM
Lance : streamlit run app.py
"""
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# IMPORTANT : Charger le .env AVANT tout le reste
load_dotenv()

from src.embeddings import OpenAIEmbeddings
from src.vectorstore import ChromaManager
from sqlalchemy import text
from config.database import get_engine

# Configuration de la page
st.set_page_config(
    page_title="Amundi RAG | Veille Réglementaire",
    page_icon="🔍",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
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
""", unsafe_allow_html=True)


@st.cache_resource
def get_chroma():
    """Cache ChromaDB manager."""
    return ChromaManager()


@st.cache_resource
def get_embeddings_client():
    """Cache OpenAI embeddings client."""
    return OpenAIEmbeddings()


@st.cache_resource
def get_openai_client():
    """Cache OpenAI client pour GPT."""
    return OpenAI()


def get_db_stats():
    """Récupère les stats de la base."""
    engine = get_engine()
    with engine.connect() as conn:
        # Total articles
        total = conn.execute(text("SELECT COUNT(*) FROM articles")).fetchone()[0]

        # Par source
        result = conn.execute(text("""
            SELECT source, COUNT(*) as count 
            FROM articles 
            GROUP BY source 
            ORDER BY count DESC
        """))
        by_source = {row[0]: row[1] for row in result}

    return total, by_source


def search_rag(query, n_results=5, source_filter=None):
    """Effectue une recherche RAG."""
    embeddings_client = get_embeddings_client()
    chroma = get_chroma()

    # Générer embedding de la question
    query_embedding = embeddings_client.embed_text(query)

    # Rechercher
    where_filter = {"source": source_filter} if source_filter else None
    results = chroma.search(
        query_embedding=query_embedding,
        n_results=n_results,
        where=where_filter
    )

    return results


def generate_answer(query, results):
    """Génère une réponse avec GPT basée sur les résultats RAG."""

    if not results["ids"] or not results["ids"][0]:
        # Aucun résultat trouvé
        return {
            "answer": "❌ Je n'ai trouvé aucun document pertinent dans ma base de données pour répondre à cette question. Essayez de reformuler votre question ou de vérifier l'orthographe.",
            "sources_used": 0,
            "model": None
        }

    # Construire le contexte à partir des résultats
    context_parts = []
    sources_info = []

    for i, (text, metadata, distance) in enumerate(zip(
        results["documents"][0][:3],  # Top 3 résultats
        results["metadatas"][0][:3],
        results["distances"][0][:3]
    ), 1):
        score = (1 - distance) * 100

        if score > 30:  # Seuil de pertinence
            context_parts.append(f"""
[Document {i}]
Source: {metadata.get('source')}
Titre: {metadata.get('title')}
Date: {metadata.get('date', 'N/A')}
Contenu: {text[:1000]}
""")
            sources_info.append({
                'source': metadata.get('source'),
                'title': metadata.get('title'),
                'url': metadata.get('url'),
                'score': score
            })

    if not context_parts:
        return {
            "answer": "⚠️ J'ai trouvé des documents mais ils ne semblent pas assez pertinents pour répondre à votre question avec confiance. Pouvez-vous reformuler votre question de manière plus précise ?",
            "sources_used": 0,
            "model": None
        }

    context = "\n\n".join(context_parts)

    # Prompt pour GPT
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

    # Appel à GPT
    client = get_openai_client()

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=1000
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources_used": len(sources_info),
        "sources_info": sources_info,
        "model": "gpt-5-nano"
    }


# Header
st.title("🔍 Amundi GEM | Assistant Réglementaire")
st.markdown("💬 *Posez vos questions, je réponds en me basant sur les documents officiels*")
st.markdown("---")

# Sidebar - Statistiques
with st.sidebar:
    st.header("📊 Base de données")

    total_articles, by_source = get_db_stats()
    chroma_docs = get_chroma().count_documents()

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

# Main content
query = st.text_area(
    "Votre question",
    placeholder="Ex: Quelle est la position de l'AFG sur la facturation électronique ?",
    help="Posez une question en français ou en anglais",
    height=100
)

# Paramètres
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

# Bouton de recherche
if st.button("🤖 Obtenir une réponse", use_container_width=True, type="primary"):
    if not query:
        st.warning("⚠️ Veuillez entrer une question")
    else:
        with st.spinner("🔍 Recherche des documents pertinents..."):
            results = search_rag(query, n_results, source_filter)

        with st.spinner("💭 Génération de la réponse..."):
            answer_data = generate_answer(query, results)

        # Afficher la réponse
        with st.container():
            st.markdown("### 💡 Réponse")
            st.markdown(answer_data['answer'])

        # Métadonnées
        if answer_data['model']:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sources utilisées", answer_data['sources_used'])
            with col2:
                st.metric("Modèle", answer_data['model'])

        # Afficher les sources si demandé
        if show_sources and answer_data['sources_used'] > 0:
            st.markdown("---")
            st.subheader("📚 Sources consultées")

            for i, source_info in enumerate(answer_data['sources_info'], 1):
                with st.expander(f"📄 Source {i} - {source_info['source']} (Score: {source_info['score']:.1f}%)"):
                    st.markdown(f"**Titre :** {source_info['title']}")
                    st.markdown(f"**URL :** [{source_info['url']}]({source_info['url']})")

        # Documents détaillés
        if show_sources and results["ids"] and results["ids"][0]:
            with st.expander("🔎 Voir tous les documents trouvés"):
                for i, (doc_id, text, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ), 1):

                    score = (1 - distance) * 100

                    st.markdown(f"**Document {i}** - Score: {score:.1f}%")
                    st.text(f"Source: {metadata.get('source')} | Date: {metadata.get('date', 'N/A')}")
                    st.text(f"Titre: {metadata.get('title')[:80]}...")
                    st.markdown(f"[Lien]({metadata.get('url')})")
                    st.markdown("---")

# Instructions
if not query:
    st.info("💡 **Comment utiliser cet assistant ?**")
    st.markdown("""
    1. **Posez votre question** dans le champ ci-dessus
    2. **Filtrez par source** si vous cherchez dans une autorité spécifique (optionnel)
    3. **Cliquez sur "Obtenir une réponse"** pour lancer la recherche
    4. **L'assistant génère une réponse** basée sur les documents officiels
    
    **Exemples de questions :**
    - "Quelle est la position de l'AFG sur la facturation électronique ?"
    - "Quelles sont les obligations de reporting EMIR 3.0 ?"
    - "Résume les principales mesures concernant les fonds d'investissement"
    - "Qu'est-ce que la grille d'impact pour la dette privée ?"
    """)

# Footer
st.markdown("---")
st.caption("🏦 Amundi Asset Management | Assistant IA de Veille Réglementaire")