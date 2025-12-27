"""
Script de recherche RAG
Lance : python scripts/search_rag.py "votre question"
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import OpenAIEmbeddings
from src.vectorstore import ChromaManager


def search(query: str, n_results: int = 5, source_filter: str = None):
    """
    Recherche des articles pertinents via RAG.

    Args:
        query: Question de l'utilisateur
        n_results: Nombre de résultats à retourner
        source_filter: Filtrer par source (ex: "ESMA")
    """
    print("\n" + "=" * 60)
    print(f"🔍 RECHERCHE RAG")
    print("=" * 60)
    print(f"\n❓ Question : {query}")

    # 1. Générer l'embedding de la question
    print("\n🤖 Génération de l'embedding de la question...")
    embeddings_client = OpenAIEmbeddings()
    query_embedding = embeddings_client.embed_text(query)

    # 2. Rechercher dans ChromaDB
    print(f"\n🔎 Recherche des {n_results} documents les plus pertinents...")
    chroma = ChromaManager()

    where_filter = {"source": source_filter} if source_filter else None
    results = chroma.search(
        query_embedding=query_embedding,
        n_results=n_results,
        where=where_filter
    )

    # 3. Afficher les résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)

    if not results["ids"] or not results["ids"][0]:
        print("\n⚠️  Aucun résultat trouvé")
        return

    for i, (doc_id, text, metadata, distance) in enumerate(zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
    ), 1):
        print(f"\n--- Résultat {i} (score: {1 - distance:.3f}) ---")
        print(f"📌 Source : {metadata.get('source')}")
        print(f"📄 Titre : {metadata.get('title')}")
        print(f"🔗 URL : {metadata.get('url')}")
        print(f"📅 Date : {metadata.get('date', 'N/A')}")
        print(f"\n📝 Extrait :")
        print(f"{text[:300]}...")

    print("\n" + "=" * 60)

    # Stats
    stats = embeddings_client.get_usage_stats()
    print(f"\n💰 Coût de la recherche : ${stats['estimated_cost_usd']:.6f}")


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("\n❌ Usage : python scripts/search_rag.py \"votre question\"")
        print("\nExemples :")
        print('  python scripts/search_rag.py "What is ESMA\'s position on crypto?"')
        print('  python scripts/search_rag.py "Réglementation AMF sur les fonds"')
        print('  python scripts/search_rag.py "CSSF Luxembourg" --source CSSF')
        return

    query = sys.argv[1]

    # Options
    n_results = 5
    source_filter = None

    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            source_filter = sys.argv[idx + 1]

    if "--n" in sys.argv:
        idx = sys.argv.index("--n")
        if idx + 1 < len(sys.argv):
            n_results = int(sys.argv[idx + 1])

    search(query, n_results, source_filter)


if __name__ == "__main__":
    main()