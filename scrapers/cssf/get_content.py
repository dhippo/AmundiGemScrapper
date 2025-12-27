import time
from bs4 import BeautifulSoup


def get_cssf_article_content(driver, url):
    """
    Extrait le contenu de la div 'content'.
    Nettoie les boutons de partage au début.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # CIBLAGE : Classe 'content' identifiée au diagnostic
        content_div = soup.find('div', class_='content')

        if content_div:
            # On récupère tout le texte
            full_text = content_div.get_text(separator='\n\n', strip=True)

            # NETTOYAGE
            # On définit ce qu'on veut virer (le header de l'article avec les partages)
            noise_start = [
                "Envoyer par email",
                "Partager sur LinkedIn",
                "Partager sur Facebook",
                "Partager sur Twitter",
                "Publié le"  # La date est déjà dans la liste, on peut l'enlever du corps si on veut
            ]

            lines = full_text.split('\n\n')
            cleaned_lines = []

            for line in lines:
                # Si la ligne contient un mot clé de bruit, on l'ignore
                if any(noise in line for noise in noise_start):
                    continue
                cleaned_lines.append(line)

            return "\n\n".join(cleaned_lines).strip()

        else:
            print(f"   ⚠️ Conteneur 'content' introuvable sur {url}")
            return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""