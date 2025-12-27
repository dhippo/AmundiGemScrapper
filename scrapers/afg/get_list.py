import time
import re
from bs4 import BeautifulSoup


def get_afg_articles_list(driver):
    # --- CONFIGURATION ---
    NB_ARTICLES_WANTED = 10  # <--- C'est ici qu'on change le nombre !
    # ---------------------

    print(f"   [AFG] Récupération des {NB_ARTICLES_WANTED} derniers articles...")
    url = "https://www.afg.asso.fr/fr/actualites/"

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    cards = soup.find_all('div', class_='card-body')

    if len(cards) == 0:
        print("   ⚠️ Liste vide, tentative attente supplémentaire...")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = soup.find_all('div', class_='card-body')

    # Petit check pour info
    print(f"   -> {len(cards)} cartes visibles sur la page.")

    articles_list = []
    count = 0

    for card_body in cards:
        # ON UTILISE LA VARIABLE ICI
        if count >= NB_ARTICLES_WANTED:
            break

        # 1. Titre
        title_tag = card_body.find('h3', class_='card-title')
        if not title_tag: continue
        title = title_tag.get_text(strip=True)

        # 2. URL & Date
        card_container = card_body.find_parent()
        if card_container:
            link_tag = card_container.find('a')
            if link_tag:
                link = link_tag.get('href')
                full_url = link if link.startswith('http') else "https://www.afg.asso.fr" + link

                if "/fr/" in full_url:
                    # 3. DATE
                    date_pub = "Date non trouvée"
                    raw_text = card_container.get_text(" ", strip=True)
                    clean_text = re.sub(r'\s+', ' ', raw_text)
                    match_date = re.search(r"(?i)Mis en ligne le\s+(.*?)(?=\s-|\s*$)", clean_text)

                    if match_date:
                        date_pub = match_date.group(0).strip()

                    articles_list.append({
                        'title': title,
                        'url': full_url,
                        'date': date_pub
                    })
                    count += 1

    print(f"   [AFG] {len(articles_list)} articles sélectionnés.")
    return articles_list