import time
from bs4 import BeautifulSoup


def get_afg_article_content(driver, url):
    """
    Extrait le contenu ou détecte si l'accès est restreint.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # 1. DÉTECTION PAYWALL / MEMBRES
        # On cherche des mots clés indiquant que la page est bloquée
        full_text = soup.get_text()
        if "réservé aux membres" in full_text or "Connectez-vous" in full_text or "Authenticate to login" in full_text:
            # On vérifie si on a quand même accès au contenu (parfois le message est là mais le contenu aussi)
            if not soup.find('div', class_='entry-content'):
                return "[CONTENU RESTREINT - AUTHENTIFICATION REQUISE]"

        # 2. EXTRACTION DU CONTENU
        content_div = soup.find('div', class_='entry-content')

        # Fallback
        if not content_div:
            content_div = soup.find('div', class_='post-content')

        if content_div:
            # On nettoie un peu les retours à la ligne multiples
            text = content_div.get_text(separator='\n\n', strip=True)
            return text
        else:
            return "[Erreur : Conteneur entry-content introuvable]"

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""