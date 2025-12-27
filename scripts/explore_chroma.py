"""
Script d'exploration de ChromaDB
Lance : python scripts/explore_chroma.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectorstore import ChromaManager


def main():
    print("\n" + "=" * 60)
    print("🔍 EXPLORATION CHROMADB")
    print("=" * 60)

    chroma = ChromaManager()

    # Stats basiques
    count = chroma.count_documents()
    print(f"\n📊 Documents totaux : {count}")

    if count == 0:
        print("\n⚠️  La collection est vide")
        print("\n💡 Vérifie :")
        print("   1. Le script run_vectorization.py s'est bien terminé")
        print("   2. Aucune erreur n'est apparue lors de l'ajout")
        print("   3. Le dossier data/chroma/ existe")
        return

    # Récupérer quelques documents
    print("\n📄 Échantillon de documents :")
    docs = chroma.get_all_documents(limit=3)

    for i, (doc_id, text, metadata) in enumerate(zip(
            docs["ids"],
            docs["documents"],
            docs["metadatas"]
    )):
        print(f"\n--- Document {i + 1} ---")
        print(f"ID: {doc_id}")
        print(f"Source: {metadata.get('source')}")
        print(f"Title: {metadata.get('title', 'N/A')[:50]}...")
        print(f"Texte: {text[:100]}...")

    # Stats par source
    print(f"\n📊 Répartition par source :")
    all_docs = chroma.get_all_documents()
    sources = {}
    for meta in all_docs["metadatas"]:
        source = meta.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1

    for source, count in sorted(sources.items()):
        print(f"   • {source}: {count} chunks")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()