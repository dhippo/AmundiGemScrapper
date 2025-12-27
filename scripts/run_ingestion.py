"""
Script d'ingestion des fichiers JSON vers MySQL
Lance depuis la racine : python scripts/run_ingestion.py
"""
import sys
import json
import os
from pathlib import Path

# Ajouter le dossier racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SOURCES_CONFIG
from config.database import test_connection
from src.database.manager import insert_article, get_articles_count, get_articles_by_source


def load_json_file(filepath):
    """Charge un fichier JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"   ❌ Erreur JSON : {e}")
        return []


def ingest_source(source_code, language):
    """Ingère tous les articles d'une source."""
    json_path = f"scrapers/{source_code}/results.json"

    if not os.path.exists(json_path):
        print(f"   ⚠️  Fichier non trouvé : {json_path}")
        return 0, 0

    articles = load_json_file(json_path)

    if not articles:
        print(f"   ⚠️  Aucun article dans {json_path}")
        return 0, 0

    inserted = 0
    skipped = 0

    for i, article in enumerate(articles, 1):
        title_preview = (article.get('title', 'Sans titre')[:40] + '..') \
            if len(article.get('title', '')) > 40 \
            else article.get('title', 'Sans titre')

        if insert_article(article, source_code, language):
            inserted += 1
            status = "✅"
        else:
            skipped += 1
            status = "⏭️ "

        print(f"      [{i}/{len(articles)}] {status} {title_preview}")

    return inserted, skipped


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 60)
    print("🚀 INGESTION JSON → MySQL")
    print("=" * 60)

    # Test connexion
    if not test_connection():
        print("\n❌ Connexion DB impossible. Vérifie Docker et la config.")
        return

    print(f"📊 Articles actuellement en base : {get_articles_count()}")
    print("\n" + "-" * 60)

    total_inserted = 0
    total_skipped = 0

    for source_code, config in SOURCES_CONFIG.items():
        if not config["enabled"]:
            continue

        print(f"\n📂 Source : {config['name']} (langue: {config['language']})")
        inserted, skipped = ingest_source(source_code, config["language"])

        total_inserted += inserted
        total_skipped += skipped

        print(f"   ✅ Insérés : {inserted}")
        print(f"   ⏭️  Ignorés : {skipped}")

    print("\n" + "=" * 60)
    print(f"🏁 INGESTION TERMINÉE")
    print(f"   📥 Total insérés : {total_inserted}")
    print(f"   ⏭️  Total ignorés : {total_skipped}")

    print(f"\n📊 Répartition par source :")
    for row in get_articles_by_source():
        print(f"   • {row[0]} : {row[1]} articles")

    print("=" * 60)


if __name__ == "__main__":
    main()