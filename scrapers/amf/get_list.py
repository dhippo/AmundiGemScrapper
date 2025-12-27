import time
from bs4 import BeautifulSoup


def get_amf_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [AMF] Récupération des {NB_ARTICLES} derniers articles...")

    url = "https://www.amf-france.org/fr/actualites-publications/actualites"

    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    articles_list = []

    # CIBLAGE : On cherche le tableau de données
    table = soup.find('table', class_='data-table-listing')
    if not table:
        print("   ⚠️ Tableau introuvable. Structure modifiée ?")
        return []

    # On récupère le corps du tableau
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    count = 0
    for row in rows:
        if count >= NB_ARTICLES: break

        # On récupère les cellules (colonnes)
        cols = row.find_all('td')

        # D'après ton diagnostic : Col 0 = Date | Col 1 = Thème | Col 2 = Titre/Lien
        if len(cols) >= 3:
            # 1. DATE
            date_pub = cols[0].get_text(strip=True)

            # 2. TITRE & URL (dans la 3ème colonne)
            title_col = cols[2]
            link_tag = title_col.find('a')

            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href')
                full_url = link if link.startswith('http') else "https://www.amf-france.org" + link

                articles_list.append({
                    'title': title,
                    'url': full_url,
                    'date': date_pub
                })
                count += 1

    print(f"   [AMF] {len(articles_list)} articles trouvés.")
    return articles_list