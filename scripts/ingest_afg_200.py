"""
Injection des 200 articles AFG dans MySQL
Lance : python scripts/ingest_afg_200.py
"""
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.database import get_engine

MONTHS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}


def parse_french_date(date_str):
    """
    Parse une date française vers format SQL.
    Ex: "24 décembre 2024" -> "2024-12-24"
    """
    if not date_str or date_str == "Date non trouvée":
        return None

    try:
        # Format: "24 décembre 2024"
        parts = date_str.strip().split()
        if len(parts) == 3:
            day = int(parts[0])
            month_name = parts[1].lower()
            year = int(parts[2])

            month = MONTHS_FR.get(month_name)
            if month:
                return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        pass

    return None


def ingest_afg_articles():
    """Injecte les articles AFG dans MySQL."""

    print("\n" + "=" * 60)
    print("📥 INJECTION DES ARTICLES AFG")
    print("=" * 60)

    # 1. Charger le JSON
    json_path = "dev_analysis/afg/afg_200_articles.json"

    print(f"\n📂 Chargement : {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"   ✅ {len(articles)} articles chargés")

    # 2. Injection
    engine = get_engine()

    insert_query = text("""
                        INSERT INTO articles (source, title, url, date_published, content, language)
                        VALUES (:source, :title, :url, :date_published, :content, :language)
                        """)

    inserted = 0
    skipped = 0
    errors = 0

    print("\n💾 Injection en base...")

    with engine.connect() as conn:
        for i, article in enumerate(articles, 1):
            title = article['title']
            title_short = title[:50] + '...' if len(title) > 50 else title

            print(f"   [{i}/{len(articles)}] {title_short}", end='')

            # Parser la date
            date_sql = parse_french_date(article['date'])

            try:
                conn.execute(insert_query, {
                    'source': 'AFG',
                    'title': article['title'],
                    'url': article['url'],
                    'date_published': date_sql,
                    'content': article['content'],
                    'language': 'fr'
                })
                conn.commit()
                inserted += 1
                print(f" ✅")

            except Exception as e:
                if "Duplicate entry" in str(e):
                    skipped += 1
                    print(f" ⏭️  (doublon)")
                else:
                    errors += 1
                    print(f" ❌ {e}")

    # 3. Vérification
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM articles WHERE source='AFG'"))
        total_afg = result.fetchone()[0]

    # 4. Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"   • Articles traités : {len(articles)}")
    print(f"   • Insérés : {inserted}")
    print(f"   • Doublons : {skipped}")
    print(f"   • Erreurs : {errors}")
    print(f"\n   • Total AFG en base : {total_afg}")
    print("=" * 60)


if __name__ == "__main__":
    ingest_afg_articles()