"""
Nouveau scraper AFG optimisé - Version de test
Objectif : Récupérer 50 articles accessibles
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.driver_setup import get_driver
from bs4 import BeautifulSoup
import time
import re


def scrape_afg_page(driver, page_num):
    """Scrape une page spécifique."""
    url = f"https://www.afg.asso.fr/fr/actualites/?prod_post%5Bpage%5D={page_num}"

    print(f"\n   📄 Page {page_num}...")
    driver.get(url)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Extraire tous les H3
    all_h3 = soup.find_all('h3', class_='card-title')

    articles = []

    for h3 in all_h3:
        title = h3.get_text(strip=True)

        # Remonter pour trouver le lien et la date
        current = h3
        link = None
        date_text = None

        for _ in range(5):
            parent = current.find_parent()
            if parent:
                # Chercher le lien
                link_tag = parent.find('a')
                if link_tag and link_tag.get('href'):
                    link = link_tag.get('href')

                    # Chercher la date dans le texte du parent
                    parent_text = parent.get_text(" ", strip=True)

                    # Pattern de date AFG
                    date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', parent_text)
                    if date_match:
                        date_text = date_match.group(1)

                    break
                current = parent

        if link:
            # Construire l'URL complète
            full_url = link if link.startswith('http') else f"https://www.afg.asso.fr{link}"

            articles.append({
                'title': title,
                'url': full_url,
                'date': date_text or "Date non trouvée"
            })

    print(f"      ✅ {len(articles)} articles extraits")
    return articles


def is_article_accessible(driver, url):
    """Vérifie si un article est accessible (non restreint)."""
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        text = soup.get_text().lower()

        # Détecter restriction
        if "réservé aux membres" in text or "authentification requise" in text:
            return False

        # Vérifier qu'il y a du contenu
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            content = content_div.get_text(strip=True)
            if len(content) > 100:  # Minimum 100 chars
                return True

        return False

    except Exception as e:
        print(f"      ⚠️  Erreur : {e}")
        return False


def get_article_content(driver, url):
    """Extrait le contenu d'un article."""
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Vérifier restriction
        text = soup.get_text().lower()
        if "réservé aux membres" in text:
            return "[CONTENU RESTREINT - AUTHENTIFICATION REQUISE]"

        # Extraire contenu
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            return content_div.get_text(separator='\n\n', strip=True)

        return "[Erreur : Contenu non trouvé]"

    except Exception as e:
        return f"[Erreur : {e}]"


def scrape_afg_50_articles():
    """Scrape 50 articles AFG accessibles."""

    print("\n" + "=" * 60)
    print("🚀 SCRAPING AFG - 50 ARTICLES")
    print("=" * 60)

    driver = get_driver()

    try:
        all_articles = []
        accessible_articles = []

        # Étape 1 : Collecter les URLs (3 pages = 60 articles)
        print("\n📋 Étape 1 : Collection des URLs...")

        for page in range(1, 4):  # Pages 1, 2, 3
            articles = scrape_afg_page(driver, page)
            all_articles.extend(articles)

            if len(all_articles) >= 60:
                break

        print(f"\n   ✅ {len(all_articles)} URLs collectées")

        # Étape 2 : Filtrer et extraire le contenu
        print("\n📝 Étape 2 : Extraction du contenu (articles accessibles)...")

        for i, article in enumerate(all_articles, 1):
            if len(accessible_articles) >= 50:
                break

            title_short = article['title'][:40] + '...'
            print(f"\n   [{i}/{len(all_articles)}] {title_short}")

            # Vérifier accessibilité
            if is_article_accessible(driver, article['url']):
                # Extraire contenu
                content = get_article_content(driver, article['url'])

                article['content'] = content
                accessible_articles.append(article)

                print(f"      ✅ Accessible ({len(content)} chars)")
            else:
                print(f"      🔒 Restreint - SKIP")

        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ")
        print("=" * 60)
        print(f"   • URLs collectées : {len(all_articles)}")
        print(f"   • Articles accessibles : {len(accessible_articles)}")
        print(f"   • Articles restreints : {len(all_articles) - len(accessible_articles)}")

        if len(accessible_articles) >= 50:
            print(f"\n   ✅ Objectif atteint : 50+ articles !")
        else:
            print(f"\n   ⚠️  Seulement {len(accessible_articles)} articles accessibles")

        # Sauvegarder pour inspection
        import json
        output_path = "dev_analysis/afg/test_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(accessible_articles[:50], f, ensure_ascii=False, indent=2)

        print(f"\n   💾 Résultats sauvegardés : {output_path}")
        print("=" * 60)

        return accessible_articles[:50]

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_afg_50_articles()