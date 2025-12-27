import sqlalchemy
from sqlalchemy import create_engine, text

# Config (Idéalement à mettre dans un .env plus tard)
DB_USER = "dhippo_user"
DB_PASS = "dhippo_password"
DB_HOST = "127.0.0.1"
DB_PORT = "3307"
DB_NAME = "amundi"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)


def save_article_to_mysql(article_data):
    """
    Sauvegarde un article en base. Ignore silencieusement les doublons d'URL.
    """
    if not article_data.get('content'):
        return  # On ne sauvegarde pas les articles vides

    query = text("""
                 INSERT
                 IGNORE INTO articles (source, title, url, date_published, content)
        VALUES (:source, :title, :url, :date, :content)
                 """)

    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "source": article_data.get('source', 'Unknown'),
                "title": article_data.get('title'),
                "url": article_data.get('url'),
                "date": article_data.get('date'),
                "content": article_data.get('content')
            })
            conn.commit()
            # print(f"   💾 Saved: {article_data['title'][:30]}...")
    except Exception as e:
        print(f"   ❌ Erreur DB: {e}")