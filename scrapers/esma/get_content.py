import time
from bs4 import BeautifulSoup


def get_esma_article_content(driver, url):
    """
    Extrait le contenu de l'article ESMA.
    Cible <article class="node--view-mode-full"> et nettoie le bruit.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # CIBLAGE : Identifié par le diagnostic (Candidat 0)
        # On cherche l'article en mode "vue complète"
        article = soup.find('article', class_='node--view-mode-full')

        if article:
            # On récupère le texte avec des sauts de ligne
            full_text = article.get_text(separator='\n\n', strip=True)

            # NETTOYAGE
            # 1. Bruit de fin de page
            stop_markers = [
                "Related Documents",
                "Download All Files",
                "Back to top",
                "Related News"
            ]
            for marker in stop_markers:
                if marker in full_text:
                    full_text = full_text.split(marker)[0]

            # 2. Bruit de début de page (Tags, date répétés)
            # On va supprimer les lignes qui contiennent ces mots clés génériques
            noise_start = [
                "About ESMA",
                "Press Releases",
                "Share this page",
                "Menu",
                "Home"
            ]

            lines = full_text.split('\n\n')
            cleaned_lines = []

            # On parcourt les lignes et on ne garde que celles qui sont du vrai texte
            for line in lines:
                # Si la ligne est exactement un des mots parasites, on saute
                if line.strip() in noise_start:
                    continue
                # Si la ligne est une date seule (04/12/2025), on saute (déjà dans la liste)
                if len(line.strip()) == 10 and "/" in line:
                    continue

                cleaned_lines.append(line)

            return "\n\n".join(cleaned_lines).strip()

        else:
            print(f"   ⚠️ Conteneur <article> introuvable sur {url}")
            return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""