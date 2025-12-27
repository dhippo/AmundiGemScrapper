import time
from bs4 import BeautifulSoup

def get_finma_article_content(driver, url):
    """
    Extrait le contenu global via le conteneur 'text-page' pour éviter de rater
    des paragraphes ou des listes situés hors des blocs 'mod-content'.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # --- CORRECTION MAJEURE ---
        # Au lieu de chercher des morceaux (mod-teaser, mod-content),
        # on cible le conteneur parent global identifié par le diagnostic.
        # Cela capture tout : le chapeau, le corps, les listes et les <span> isolés.
        content_div = soup.find('div', class_='text-page')

        full_text = ""

        if content_div:
            # separator='\n\n' est CRUCIAL pour que la liste des membres
            # (Mirjam Eggen, etc.) ne soit pas collée en une seule ligne.
            full_text = content_div.get_text(separator='\n\n', strip=True)
        else:
            # Fallback : Si 'text-page' n'existe pas (anciennes pages ?),
            # on tente une extraction brute du body ou on log l'erreur.
            print(f"   ⚠️ Conteneur 'text-page' introuvable sur {url}")
            return ""

        # --- NETTOYAGE DU PIED DE PAGE ---
        # Le conteneur 'text-page' inclut souvent le footer technique,
        # donc ce nettoyage reste indispensable.
        stop_markers = [
            "Dernière modification", # J'ai retiré le ':' pour être plus large
            "Taille:",
            "Langue(s):",
            "Contact\n",
            "Autorité fédérale de surveillance des marchés financiers FINMA"
        ]

        for marker in stop_markers:
            if marker in full_text:
                full_text = full_text.split(marker)[0]

        return full_text.strip()

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""