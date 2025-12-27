import time
import re
from bs4 import BeautifulSoup


def get_finma_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [FINMA] Récupération des {NB_ARTICLES} derniers articles...")

    url = "https://www.finma.ch/fr/news/"

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    articles_list = []

    cards = soup.find_all('div', class_='teaser-news')

    count = 0
    for card in cards:
        if count >= NB_ARTICLES: break

        title_link = card.find('a', class_='teaser-content-title')

        if title_link:
            title = title_link.get_text(strip=True)
            link = title_link.get('href', '')

            # --- FILTRE DE SÉCURITÉ RENFORCÉ ---
            # Si le titre ou le lien contient des accolades de template ou est vide
            if not link or "{{" in link or "{{" in title:
                continue
            # -----------------------------------

            full_url = link if link.startswith('http') else "https://www.finma.ch" + link

            date_pub = "Date non trouvée"
            card_text = card.get_text(" | ", strip=True)
            match_date = re.search(r"(\d{1,2}\s+[a-zéû]+\s+\d{4})", card_text)

            if match_date:
                date_pub = match_date.group(0)

            articles_list.append({
                'title': title,
                'url': full_url,
                'date': date_pub
            })
            count += 1

    print(f"   [FINMA] {len(articles_list)} articles trouvés.")
    return articles_list