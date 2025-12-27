"""
Database Manager - Gestion des opérations de base de données
"""
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from config.database import get_engine
from datetime import datetime


def clean_date(date_str):
    """
    Nettoie et normalise les dates au format SQL (YYYY-MM-DD).
    Retourne None si la date n'est pas parsable.
    """
    if not date_str or date_str.strip() == "":
        return None

    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%d %B %Y",
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def insert_article(article_data, source_code, language):
    """
    Insère un article dans la base de données.
    Retourne True si inséré, False si doublon (URL existante).
    """
    query = text("""
                 INSERT INTO articles (source, title, url, date_published, content, language)
                 VALUES (:source, :title, :url, :date_published, :content, :language)
                 """)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(query, {
                "source": source_code.upper(),
                "title": article_data.get("title", "Sans titre"),
                "url": article_data.get("url", ""),
                "date_published": clean_date(article_data.get("date", "")),
                "content": article_data.get("content", ""),
                "language": language
            })
            conn.commit()
        return True
    except IntegrityError:
        # URL déjà existante (duplicate)
        return False
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        return False


def get_articles_count():
    """Retourne le nombre total d'articles en base."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as count FROM articles"))
        return result.fetchone()[0]


def get_articles_by_source():
    """Retourne la répartition des articles par source."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
                                   SELECT source, COUNT(*) as count
                                   FROM articles
                                   GROUP BY source
                                   ORDER BY source
                                   """))
        return result.fetchall()