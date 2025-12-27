"""
Nettoyage de ChromaDB
Lance : python scripts/clean_chromadb.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore import ChromaManager


def clean_chromadb():
    """Supprime tous les embeddings de ChromaDB."""

    print("\n" + "=" * 60)
    print("🧹 NETTOYAGE CHROMADB")
    print("=" * 60)

    chroma = ChromaManager()
    count = chroma.count_documents()

    print(f"\n📊 État actuel : {count} documents")

    if count == 0:
        print("   ✅ ChromaDB est déjà vide")
        return

    # Répartition
    docs = chroma.get_all_documents()
    sources = {}
    for meta in docs["metadatas"]:
        source = meta.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1

    print("\n   Répartition :")
    for source, cnt in sorted(sources.items()):
        print(f"      • {source}: {cnt} chunks")

    # Confirmation
    print("\n" + "⚠️ " * 20)
    response = input("\n👉 Supprimer tous les embeddings ? (tapez 'DELETE'): ").strip()

    if response != 'DELETE':
        print("\n❌ Annulé")
        return

    # Suppression
    chroma.reset_collection()

    final_count = chroma.count_documents()

    print("\n" + "=" * 60)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 60)
    print(f"   • Supprimés : {count}")
    print(f"   • Restants : {final_count}")
    print("=" * 60)


if __name__ == "__main__":
    clean_chromadb()