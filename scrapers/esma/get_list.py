import time
import re
from bs4 import BeautifulSoup


def get_esma_articles_list(driver):
    NB_ARTICLES = 5
    print(f"   [ESMA] Récupération des {NB_ARTICLES} derniers articles...")

    url = "https://www.esma.europa.eu/press-news/esma-news"
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    articles_list = []
    cards = soup.find_all('div', class_='search-card')

    count = 0
    for card in cards:
        if count >= NB_ARTICLES: break

        title_div = card.find('div', class_='search-title')
        if not title_div: continue
        title = title_div.get_text(strip=True)

        link_tag = card.find('a')
        if not link_tag: link_tag = title_div.find('a')

        if link_tag:
            link = link_tag.get('href')
            full_url = link if link.startswith('http') else "https://www.esma.europa.eu" + link

            date_pub = "Date non trouvée"
            time_tag = card.find('time')
            if time_tag:
                date_pub = time_tag.get_text(strip=True)
            else:
                card_text = card.get_text(" | ", strip=True)
                match_date = re.search(r"(\d{2}/\d{2}/\d{4})", card_text)
                if match_date: date_pub = match_date.group(0)

            articles_list.append({
                'title': title, 'url': full_url, 'date': date_pub
            })
            count += 1

    print(f"   [ESMA] {len(articles_list)} articles trouvés.")
    return articles_list