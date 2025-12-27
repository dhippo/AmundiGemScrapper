"""
Script de vectorisation des articles MySQL → ChromaDB
Lance : python scripts/run_vectorization.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le dossier racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.database import get_engine
from src.embeddings import split_text_into_chunks, estimate_cost, OpenAIEmbeddings
from src.vectorstore import ChromaManager


def load_articles_from_db():
    """Charge tous les articles depuis MySQL."""
    engine = get_engine()
    query = text("""
                 SELECT id, source, title, url, date_published, content, language
                 FROM articles
                 WHERE content IS NOT NULL AND content != ''
                 ORDER BY id
                 """)

    with engine.connect() as conn:
        result = conn.execute(query)
        articles = [dict(row._mapping) for row in result]

    return articles


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 60)
    print("🚀 VECTORISATION DES ARTICLES")
    print("=" * 60)

    # 1. Charger les articles
    print("\n📂 Chargement des articles depuis MySQL...")
    articles = load_articles_from_db()
    print(f"   ✅ {len(articles)} articles chargés")

    if not articles:
        print("   ⚠️  Aucun article à vectoriser")
        return

    # 2. Chunking
    print("\n✂️  Découpage des articles en chunks...")
    all_chunks = []
    total_tokens = 0

    for article in articles:
        metadata = {
            "article_id": article["id"],
            "source": article["source"],
            "title": article["title"],
            "url": article["url"],
            "date": str(article["date_published"]) if article["date_published"] else None,
            "language": article["language"]
        }

        chunks = split_text_into_chunks(article["content"], metadata)
        all_chunks.extend(chunks)
        total_tokens += sum(chunk["token_count"] for chunk in chunks)

    print(f"   ✅ {len(all_chunks)} chunks créés")
    print(f"   📊 Total tokens : {total_tokens:,}")
    print(f"   💰 Coût estimé : ${estimate_cost(total_tokens):.4f}")

    # 3. Confirmation
    response = input("\n👉 Continuer avec la vectorisation ? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Vectorisation annulée")
        return

    # 4. Génération des embeddings
    print("\n🤖 Génération des embeddings via OpenAI...")
    embeddings_client = OpenAIEmbeddings()

    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embeddings_client.embed_batch(texts)

    # 5. Stockage dans ChromaDB
    print("\n💾 Stockage dans ChromaDB...")
    chroma = ChromaManager()

    # Réinitialiser la collection si demandé
    if chroma.count_documents() > 0:
        print(f"   ⚠️  La collection contient déjà {chroma.count_documents()} documents")
        response = input("   👉 Réinitialiser ? (y/n): ").lower().strip()
        if response == 'y':
            chroma.reset_collection()

    # Préparer les données (filtrer les None des métadonnées)
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    metadatas = []

    for chunk in all_chunks:
        # Filtrer les valeurs None
        clean_metadata = {
            k: v for k, v in chunk["metadata"].items()
            if v is not None
        }
        metadatas.append(clean_metadata)

    # DEBUG
    print(f"\n🔍 DEBUG:")
    print(f"   len(texts) = {len(texts)}")
    print(f"   len(embeddings) = {len(embeddings)}")
    print(f"   len(metadatas) = {len(metadatas)}")
    print(f"   len(ids) = {len(ids)}")
    print(f"   Exemple metadata: {metadatas[0] if metadatas else 'VIDE'}")

    # Ajouter par batch pour éviter les timeouts
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        end_idx = min(i + batch_size, len(texts))
        print(f"   Ajout batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}...")

        chroma.add_documents(
            texts=texts[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )

    # 6. Statistiques finales
    print("\n" + "=" * 60)
    print("✅ VECTORISATION TERMINÉE")
    print("=" * 60)

    stats = embeddings_client.get_usage_stats()
    print(f"\n📊 Statistiques :")
    print(f"   • Articles traités : {len(articles)}")
    print(f"   • Chunks créés : {len(all_chunks)}")
    print(f"   • Tokens utilisés : {stats['total_tokens']:,}")
    print(f"   • Coût total : ${stats['estimated_cost_usd']:.4f}")
    print(f"   • Documents dans ChromaDB : {chroma.count_documents()}")

    print("\n🎯 Prochaine étape : python scripts/search_rag.py")
    print("=" * 60)


if __name__ == "__main__":
    main()