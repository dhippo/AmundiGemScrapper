import time
import re
from bs4 import BeautifulSoup


def get_cssf_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [CSSF] Récupération des {NB_ARTICLES} derniers articles...")

    url = "https://www.cssf.lu/fr/news-fr/"

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    articles_list = []

    # CIBLAGE : On utilise la classe 'article-card' identifiée au diagnostic
    cards = soup.find_all('div', class_='article-card')

    count = 0
    for card in cards:
        if count >= NB_ARTICLES: break

        # 1. TITRE (h3)
        title_tag = card.find('h3')
        if not title_tag: continue
        title = title_tag.get_text(strip=True)

        # 2. LIEN
        # Le lien est souvent sur le titre ou autour de la carte
        link_tag = card.find('a')
        if link_tag:
            link = link_tag.get('href')
            full_url = link if link.startswith('http') else "https://www.cssf.lu" + link

            # 3. DATE
            # Format vu : "2 décembre 2025 - Communiqué de presse"
            # La date est souvent dans une div 'meta' ou juste un paragraphe p
            date_pub = "Date non trouvée"

            # On cherche le texte qui commence par un chiffre
            card_text = card.get_text(" | ", strip=True)
            # Regex : Chiffre + espace + mot + espace + 4 chiffres
            match_date = re.search(r"(\d{1,2}\s+[a-zéû]+\s+\d{4})", card_text)

            if match_date:
                date_pub = match_date.group(0)  # "2 décembre 2025"

            articles_list.append({
                'title': title,
                'url': full_url,
                'date': date_pub
            })
            count += 1

    print(f"   [CSSF] {len(articles_list)} articles trouvés.")
    return articles_list