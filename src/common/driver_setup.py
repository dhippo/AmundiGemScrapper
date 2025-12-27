"""
Configuration du driver Selenium pour le scraping
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import SELENIUM_CONFIG


def get_driver():
    """Configure et renvoie le driver Selenium standardisé pour le projet."""
    chrome_options = Options()

    if SELENIUM_CONFIG["headless"]:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--window-size={SELENIUM_CONFIG['window_size']}")
    chrome_options.add_argument(f"user-agent={SELENIUM_CONFIG['user_agent']}")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)