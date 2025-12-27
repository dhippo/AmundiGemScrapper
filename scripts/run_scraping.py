"""
Script de scraping des sources configurées
Lance depuis la racine : python scripts/run_scraping.py
"""
import sys
import json
import os
import time
from pathlib import Path

# Ajouter le dossier racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SOURCES_CONFIG
from src.common.driver_setup import get_driver

# Imports dynamiques des scrapers
from scrapers.afg.get_list import get_afg_articles_list
from scrapers.afg.get_content import get_afg_article_content
from scrapers.afm.get_list import get_afm_articles_list
from scrapers.afm.get_content import get_afm_article_content
from scrapers.alfi.get_list import get_alfi_articles_list
from scrapers.alfi.get_content import get_alfi_article_content
from scrapers.amf.get_list import get_amf_articles_list
from scrapers.amf.get_content import get_amf_article_content
from scrapers.cbi.get_list import get_cbi_articles_list
from scrapers.cbi.get_content import get_cbi_article_content
from scrapers.cssf.get_list import get_cssf_articles_list
from scrapers.cssf.get_content import get_cssf_article_content
from scrapers.esma.get_list import get_esma_articles_list
from scrapers.esma.get_content import get_esma_article_content
from scrapers.finma.get_list import get_finma_articles_list
from scrapers.finma.get_content import get_finma_article_content

SCRAPER_FUNCTIONS = {
    "afg": {"list": get_afg_articles_list, "content": get_afg_article_content},
    "afm": {"list": get_afm_articles_list, "content": get_afm_article_content},
    "alfi": {"list": get_alfi_articles_list, "content": get_alfi_article_content},
    "amf": {"list": get_amf_articles_list, "content": get_amf_article_content},
    "cbi": {"list": get_cbi_articles_list, "content": get_cbi_article_content},
    "cssf": {"list": get_cssf_articles_list, "content": get_cssf_article_content},
    "esma": {"list": get_esma_articles_list, "content": get_esma_article_content},
    "finma": {"list": get_finma_articles_list, "content": get_finma_article_content},
}


def save_results(data, filepath):
    """Sauvegarde les données en JSON."""
    if data:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"   💾 Sauvegardé : {filepath}")
        except Exception as e:
            print(f"   ❌ Erreur sauvegarde : {e}")


def scrape_source(source_code, config, driver):
    """Scrape une source donnée."""
    print(f"\n{'=' * 60}")
    print(f"🚀 LANCEMENT : {config['name']}")
    print("=" * 60)

    functions = SCRAPER_FUNCTIONS[source_code]
    result_path = f"scrapers/{source_code}/results.json"

    try:
        # Récupération de la liste
        print(f"   ... Récupération de la liste des articles")
        items = functions["list"](driver)

        if not items:
            print(f"   ⚠️  Aucun article trouvé")
            return

        data = []
        print(f"   ... Extraction du contenu pour {len(items)} articles")

        # Récupération du contenu
        for i, item in enumerate(items, 1):
            title_preview = (item['title'][:50] + '..') if len(item['title']) > 50 else item['title']
            print(f"      [{i}/{len(items)}] {title_preview}")

            try:
                content = functions["content"](driver, item['url'])
                status = "✅" if content and len(content) > 50 else "⚠️"
                print(f"          {status} Contenu récupéré ({len(content)} cars)")
                data.append({**item, "content": content})
            except Exception as e:
                print(f"          ❌ Erreur : {e}")
                data.append({**item, "content": "", "error": str(e)})

        # Sauvegarde
        save_results(data, result_path)
        print(f"✅ Module {config['name']} terminé")

    except Exception as e:
        print(f"❌ ERREUR : {e}")


def main():
    """Point d'entrée principal."""
    print("\n" + "#" * 60)
    print("🚀 PIPELINE DE SCRAPING AMUNDI")
    print("#" * 60)

    driver = get_driver()
    start_time = time.time()

    try:
        for source_code, config in SOURCES_CONFIG.items():
            if config["enabled"]:
                scrape_source(source_code, config, driver)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel détecté !")
    except Exception as e:
        print(f"\n❌ Erreur globale : {e}")
    finally:
        print("\n" + "-" * 30)
        print("🧹 Fermeture du driver...")
        driver.quit()
        duration = time.time() - start_time
        print(f"🏁 Terminé en {duration:.2f}s")
        print("-" * 30)


if __name__ == "__main__":
    main()