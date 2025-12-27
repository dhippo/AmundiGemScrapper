import time
import re
from bs4 import BeautifulSoup


def get_alfi_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [ALFI] Récupération des {NB_ARTICLES} derniers articles...")

    # Page news ALFI
    url = "https://www.alfi.lu/en-gb/news/1"

    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # CIBLAGE : On prend les balises <a> qui ont la classe 'card'
    # (Identifié via ton diagnostic précédent Niveau -3)
    cards = soup.find_all('a', class_='card')

    articles_list = []
    count = 0

    for card in cards:
        if count >= NB_ARTICLES: break

        # 1. URL
        link = card.get('href')
        if not link: continue
        full_url = link if link.startswith('http') else "https://www.alfi.lu" + link

        # 2. Titre (dans le h3)
        title_tag = card.find('h3')
        title = title_tag.get_text(strip=True) if title_tag else "Titre inconnu"

        # 3. Date
        # Format "14 October 2025 | Statements..."
        # On cherche un motif : Chiffre(s) + Mois + Année (4 chiffres)
        date_pub = "Date non trouvée"
        raw_text = card.get_text(" ", strip=True)
        # Regex : 1 ou 2 chiffres + espace + mot (Mois) + espace + 4 chiffres
        match_date = re.search(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})", raw_text)
        if match_date:
            date_pub = match_date.group(0)

        articles_list.append({
            'title': title,
            'url': full_url,
            'date': date_pub
        })
        count += 1

    print(f"   [ALFI] {len(articles_list)} articles trouvés.")
    return articles_list