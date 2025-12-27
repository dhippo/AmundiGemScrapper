import time
from bs4 import BeautifulSoup


def get_alfi_article_content(driver, url):
    """
    Extrait le contenu de la section 'wrapper-news-detail'.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # CIBLAGE : Identifié par le diagnostic (Niveau 1)
        content_section = soup.find('section', class_='wrapper-news-detail')

        if content_section:
            full_text = content_section.get_text(separator='\n\n', strip=True)

            # NETTOYAGE
            # On coupe le bas de page inutile
            stop_markers = ["Back", "JOIN THE ALFI COMMUNITY", "Related documents"]
            for marker in stop_markers:
                if marker in full_text:
                    full_text = full_text.split(marker)[0]

            return full_text.strip()
        else:
            print(f"   ⚠️ Section 'wrapper-news-detail' introuvable sur {url}")
            return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""