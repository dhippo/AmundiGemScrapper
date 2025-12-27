import time
from bs4 import BeautifulSoup


def get_cbi_article_content(driver, url):
    """
    Extrait le contenu pour Central Bank of Ireland (CMS Sitefinity).
    Stratégie : Chercher les conteneurs standards du CMS (sf_colsIn).
    """
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        full_text = ""

        # --- STRATÉGIE 1 : Conteneurs Sitefinity (Standard) ---
        # Le contenu éditorial est souvent dans <div class="sf_colsIn">
        content_divs = soup.find_all('div', class_='sf_colsIn')

        if content_divs:
            # On prend le div qui contient le plus de texte (pour éviter les sidebars)
            main_div = max(content_divs, key=lambda d: len(d.get_text()))
            full_text = main_div.get_text(separator='\n\n', strip=True)

        # --- STRATÉGIE 2 : Fallback sur 'article' ou 'main' ---
        if len(full_text) < 50:
            fallback = soup.find('article') or soup.find('main')
            if fallback:
                full_text = fallback.get_text(separator='\n\n', strip=True)

        # --- NETTOYAGE ---
        if full_text:
            # Nettoyage des parasites courants sur ce site
            stop_phrases = [
                "Share this page",
                "Cookie Policy",
                "See Also:",
                "Notes to Editor"
            ]

            cleaned_lines = []
            for line in full_text.split('\n'):
                # On enlève les lignes vides ou qui contiennent des phrases parasites
                if line.strip() and not any(phrase in line for phrase in stop_phrases):
                    cleaned_lines.append(line.strip())

            return "\n".join(cleaned_lines)

        return ""

    except Exception as e:
        print(f"   ⚠️ Erreur contenu {url}: {e}")
        return ""