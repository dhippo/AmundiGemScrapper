# Architecture Technique - Amundi GEM RAG

## Vue d'ensemble du pipeline
```
[Sites Web] → [Scrapers] → [JSON] → [MySQL] → [Vectorisation] → [ChromaDB]
                                                                      ↓
                                                              [Interface RAG]
```

## Modules détaillés

### 1. Scrapers (`scrapers/[source]/`)
Chaque source a sa structure propre :
- `get_list.py` : Récupère la liste des URLs
- `get_content.py` : Extrait le contenu de chaque article
- `results.json` : Sortie intermédiaire

### 2. Common (`common/`)
- `driver_setup.py` : Configuration Selenium
- `db_manager.py` : Gestionnaire de connexion MySQL
- `migrations/` : Scripts de migration DB

### 3. Base de données

#### Schema MySQL
```sql
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source VARCHAR(50),
    title VARCHAR(500),
    url TEXT,
    date_published DATETIME,
    content LONGTEXT,
    language VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_date (date_published)
);
```

#### ChromaDB (à venir)
Collections prévues :
- `regulatory_articles` : Embeddings des articles
- Métadonnées : source, date, language, url