"""
Script de nettoyage de la base de données
Lance : python scripts/clean_database.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.database import get_engine


def clean_database():
    """Supprime toutes les données de la table articles."""

    print("\n" + "=" * 60)
    print("🧹 NETTOYAGE DE LA BASE DE DONNÉES")
    print("=" * 60)

    engine = get_engine()

    try:
        # 1. Afficher l'état actuel
        with engine.connect() as conn:
            # Compter total
            result = conn.execute(text("SELECT COUNT(*) as count FROM articles"))
            total = result.fetchone()[0]

            print(f"\n📊 État actuel :")
            print(f"   • Total articles : {total}")

            if total > 0:
                # Répartition par source
                result = conn.execute(text("""
                                           SELECT source, COUNT(*) as count
                                           FROM articles
                                           GROUP BY source
                                           ORDER BY source
                                           """))

                print(f"\n   Répartition par source :")
                for row in result:
                    print(f"      • {row[0]} : {row[1]} articles")

        if total == 0:
            print("\n   ✅ La base est déjà vide")
            return

        # 2. Confirmation
        print("\n" + "⚠️ " * 20)
        print("ATTENTION : Cette action va supprimer TOUS les articles !")
        print("⚠️ " * 20)

        response = input("\n👉 Confirmer la suppression ? (tapez 'DELETE' pour confirmer): ").strip()

        if response != 'DELETE':
            print("\n❌ Opération annulée")
            return

        # 3. Suppression
        print("\n🗑️  Suppression en cours...")

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE articles"))
            conn.commit()

        # 4. Vérification
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM articles"))
            final_count = result.fetchone()[0]

        print("\n" + "=" * 60)
        print("✅ NETTOYAGE TERMINÉ")
        print("=" * 60)
        print(f"   • Articles supprimés : {total}")
        print(f"   • Articles restants : {final_count}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        raise


if __name__ == "__main__":
    clean_database()