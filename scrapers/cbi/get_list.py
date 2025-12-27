import time
import re
from bs4 import BeautifulSoup


def get_cbi_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [CBI] Récupération des {NB_ARTICLES} derniers articles...")

    url = "https://www.centralbank.ie/news-media/press-releases"

    try:
        driver.get(url)
        # Le site semble charger des éléments dynamiquement ou via des composants JS
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        articles_list = []

        # Basé sur le diagnostic : GRAND-PARENT = class 'spotlight'
        # On cherche tous les blocs qui contiennent "spotlight"
        cards = soup.find_all('div', class_='spotlight')

        count = 0
        for card in cards:
            if count >= NB_ARTICLES: break

            # Basé sur le diagnostic : PARENT direct = class 'spotlight-content'
            content_div = card.find('div', class_='spotlight-content')

            if not content_div:
                continue

            # Le lien <a> est dans spotlight-content
            link_tag = content_div.find('a')

            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag.get('href', '')

                # Vérification si le lien est valide
                if not href or href == "#":
                    continue

                # Gestion des URLs relatives vs absolues
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = "https://www.centralbank.ie" + href

                # Extraction de la date via Regex sur tout le texte de la carte
                # Format observé : "05 December 2025"
                date_pub = "Date non trouvée"
                card_text = card.get_text(" ", strip=True)

                # Regex pour : 1 ou 2 chiffres + espace + Mot (Mois) + espace + 4 chiffres
                match_date = re.search(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})", card_text)

                if match_date:
                    date_pub = match_date.group(1)

                articles_list.append({
                    'title': title,
                    'url': full_url,
                    'date': date_pub
                })
                count += 1

        print(f"   [CBI] {len(articles_list)} articles trouvés.")
        return articles_list

    except Exception as e:
        print(f"   ⚠️ Erreur lors de la récupération de la liste CBI: {e}")
        return []