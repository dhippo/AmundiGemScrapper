import time
import re
from bs4 import BeautifulSoup


def get_afm_articles_list(driver):
    # Nombre d'articles à récupérer
    NB_ARTICLES_WANTED = 5

    print(f"   [AFM] Récupération des {NB_ARTICLES_WANTED} derniers articles...")
    url = "https://www.afm.nl/en/sector/actueel"

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    # CIBLAGE : On utilise la classe identifiée au niveau -4 du diagnostic
    # La classe est souvent multiple : "cc-em cc-em--article"
    # On cherche toutes les div qui ont la classe 'cc-em--article'
    cards = soup.find_all('div', class_='cc-em--article')

    print(f"   -> {len(cards)} cartes trouvées sur la page.")

    articles_list = []
    count = 0

    for card in cards:
        if count >= NB_ARTICLES_WANTED:
            break

        # 1. Titre
        # Identifié au diagnostic : h2 class='cc-em--article__body__title'
        title_tag = card.find('h2', class_='cc-em--article__body__title')
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        # 2. URL
        # Le lien est souvent un parent du h2 ou à l'intérieur
        link_tag = card.find('a')
        if link_tag:
            link = link_tag.get('href')
            # Correction url relative
            full_url = link if link.startswith('http') else "https://www.afm.nl" + link

            # 3. DATE
            # Format vu : "03/12/25"
            date_pub = "Date non trouvée"
            card_text = card.get_text(" ", strip=True)

            # Regex : cherche 2 chiffres / 2 chiffres / 2 chiffres
            match_date = re.search(r"(\d{2}/\d{2}/\d{2})", card_text)
            if match_date:
                date_pub = match_date.group(0)

            articles_list.append({
                'title': title,
                'url': full_url,
                'date': date_pub
            })
            count += 1

    print(f"   [AFM] {len(articles_list)} articles sélectionnés.")
    return articles_list