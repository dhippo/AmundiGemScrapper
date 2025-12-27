"""
Scraper AFG - 200 articles accessibles
Avec sauvegarde progressive et reprise possible
"""
import sys
from pathlib import Path
import json
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.driver_setup import get_driver
from bs4 import BeautifulSoup
import time
import re

CHECKPOINT_FILE = "dev_analysis/afg/checkpoint_200.json"
FINAL_OUTPUT = "dev_analysis/afg/afg_200_articles.json"


def load_checkpoint():
    """Charge le checkpoint s'il existe."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_checkpoint(articles):
    """Sauvegarde un checkpoint."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def scrape_page(driver, page_num):
    """Scrape une page."""
    url = f"https://www.afg.asso.fr/fr/actualites/?prod_post%5Bpage%5D={page_num}"

    driver.get(url)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    all_h3 = soup.find_all('h3', class_='card-title')

    articles = []

    for h3 in all_h3:
        title = h3.get_text(strip=True)
        current = h3
        link = None
        date_text = None

        for _ in range(5):
            parent = current.find_parent()
            if parent:
                link_tag = parent.find('a')
                if link_tag and link_tag.get('href'):
                    link = link_tag.get('href')
                    parent_text = parent.get_text(" ", strip=True)
                    date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', parent_text)
                    if date_match:
                        date_text = date_match.group(1)
                    break
                current = parent

        if link:
            full_url = link if link.startswith('http') else f"https://www.afg.asso.fr{link}"
            articles.append({
                'title': title,
                'url': full_url,
                'date': date_text or "Date non trouvée",
                'content': None  # À remplir plus tard
            })

    return articles


def get_article_content(driver, url):
    """Extrait le contenu."""
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        text = soup.get_text().lower()

        if "réservé aux membres" in text:
            return None  # Article restreint

        content_div = soup.find('div', class_='entry-content')
        if content_div:
            content = content_div.get_text(separator='\n\n', strip=True)
            if len(content) > 100:
                return content

        return None

    except Exception as e:
        print(f"      ❌ Erreur : {e}")
        return None


def scrape_200_articles():
    """Scrape 200 articles accessibles."""

    print("\n" + "=" * 60)
    print("🚀 SCRAPING AFG - 200 ARTICLES")
    print("=" * 60)

    # Charger checkpoint
    existing = load_checkpoint()
    if existing:
        print(f"\n📂 Checkpoint trouvé : {len(existing)} articles déjà scraped")
        response = input("   Reprendre depuis le checkpoint ? (y/n): ").lower().strip()
        if response != 'y':
            existing = []

    driver = get_driver()

    try:
        accessible_articles = existing
        urls_seen = {a['url'] for a in existing}

        page = 1
        max_pages = 15  # ~300 articles pour être sûr

        print("\n📋 Phase 1 : Collection + Extraction...")

        while len(accessible_articles) < 200 and page <= max_pages:
            print(f"\n   📄 Page {page}...")

            # Scraper la page
            page_articles = scrape_page(driver, page)
            print(f"      • {len(page_articles)} articles trouvés")

            # Traiter chaque article
            new_count = 0
            for article in page_articles:
                # Skip si déjà traité
                if article['url'] in urls_seen:
                    continue

                urls_seen.add(article['url'])

                # Extraire contenu
                title_short = article['title'][:40] + '...'
                print(f"      [{len(accessible_articles) + 1}/200] {title_short}", end='')

                content = get_article_content(driver, article['url'])

                if content:
                    article['content'] = content
                    accessible_articles.append(article)
                    new_count += 1
                    print(f" ✅ ({len(content)} chars)")

                    # Checkpoint tous les 10 articles
                    if len(accessible_articles) % 10 == 0:
                        save_checkpoint(accessible_articles)
                else:
                    print(f" 🔒 Restreint")

                # Stop si objectif atteint
                if len(accessible_articles) >= 200:
                    break

            print(f"      ✅ +{new_count} articles accessibles")

            # Checkpoint de fin de page
            save_checkpoint(accessible_articles)

            page += 1

        # Sauvegarder le résultat final
        final_articles = accessible_articles[:200]

        with open(FINAL_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, ensure_ascii=False, indent=2)

        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ FINAL")
        print("=" * 60)
        print(f"   • Pages parcourues : {page - 1}")
        print(f"   • Articles accessibles : {len(accessible_articles)}")
        print(f"   • Objectif : {'✅ ATTEINT' if len(accessible_articles) >= 200 else '⚠️  PARTIEL'}")
        print(f"\n   💾 Fichier final : {FINAL_OUTPUT}")

        # Nettoyer le checkpoint
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            print(f"   🧹 Checkpoint supprimé")

        print("=" * 60)

        return final_articles

    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTION MANUELLE")
        print(f"   💾 Progression sauvegardée : {len(accessible_articles)} articles")
        print(f"   📂 Checkpoint : {CHECKPOINT_FILE}")
        print("   ▶️  Relance le script pour reprendre")
        save_checkpoint(accessible_articles)

    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        print(f"   💾 Sauvegarde d'urgence : {len(accessible_articles)} articles")
        save_checkpoint(accessible_articles)
        raise

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_200_articles()