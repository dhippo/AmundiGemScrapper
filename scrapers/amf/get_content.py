import time
from bs4 import BeautifulSoup


def get_amf_article_content(driver, url):
    """
    Extrait le contenu de l'article AMF.
    Cible la div 'contentToc' ou 'field--name-body'.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # CIBLAGE : Basé sur ton diagnostic (Niveau -2)
        content_div = soup.find('div', class_='contentToc')

        # Fallback : Si contentToc n'existe pas, on cherche le standard Drupal
        if not content_div:
            content_div = soup.find('div', class_=lambda x: x and 'field--name-body' in x)

        if content_div:
            full_text = content_div.get_text(separator='\n\n', strip=True)

            # NETTOYAGE DU BAS DE PAGE
            stop_markers = [
                "Mots clés",
                "Sur le même thème",
                "S'abonner à nos alertes",
                "Revenir en haut de page"
            ]

            for marker in stop_markers:
                if marker in full_text:
                    full_text = full_text.split(marker)[0]

            return full_text.strip()
        else:
            print(f"   ⚠️ Conteneur introuvable sur {url}")
            return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""