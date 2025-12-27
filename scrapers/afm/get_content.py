import time
from bs4 import BeautifulSoup


def get_afm_article_content(driver, url):
    """
    Extrait le contenu texte de l'article AFM.
    Coupe le texte avant les sections "More information" ou "Contact".
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # CIBLAGE : On utilise le <main> identifié par le diagnostic
        # On essaie la classe précise, sinon on prend le main tout court
        content_container = soup.find('main', class_='cc-page__content')
        if not content_container:
            content_container = soup.find('main')

        if content_container:
            # On récupère tout le texte avec des sauts de ligne pour aérer
            # Cela capture les <p>, les <ul>, les <h2>, etc.
            full_text = content_container.get_text(separator='\n\n', strip=True)

            # NETTOYAGE DU PIED DE PAGE
            # On définit des marqueurs de fin. Dès qu'on en voit un, on coupe tout ce qui suit.
            stop_markers = [
                "More information",
                "Contact for this article",
                "Tags\nSustainability"
            ]

            for marker in stop_markers:
                if marker in full_text:
                    # On ne garde que la partie GAUCHE du marqueur (avant le marqueur)
                    full_text = full_text.split(marker)[0]

            # Petit nettoyage final des espaces en trop à la fin
            return full_text.strip()

        else:
            print(f"   ⚠️ Conteneur <main> introuvable sur {url}")
            return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""