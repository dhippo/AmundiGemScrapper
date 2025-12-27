# Amundi GEM Regulatory Intelligence RAG

Plateforme d'intelligence artificielle pour la veille réglementaire européenne avec recherche sémantique (RAG).

## 🎯 Vue d'ensemble

Ce projet collecte, indexe et permet d'interroger en langage naturel les publications de 8 autorités financières européennes via :
- **Web Scraping** automatisé
- **Base MySQL** pour le stockage structuré
- **ChromaDB** pour la recherche vectorielle
- **OpenAI Embeddings** pour la compréhension sémantique

---

## 🏗️ Architecture

```
Scraping → MySQL → Vectorisation → ChromaDB → Recherche RAG
```

### Stack Technique
- **Python 3.13**
- **MySQL 8.0** (Docker)
- **ChromaDB 1.3.7** (local)
- **OpenAI API** (text-embedding-3-small)
- **Selenium** + BeautifulSoup4

---

## 🌍 Sources Surveillées

| Source | Pays/Zone | Langue | Articles |
|--------|-----------|--------|----------|
| AFG | 🇫🇷 France | FR | 10 |
| AFM | 🇳🇱 Pays-Bas | EN | 5 |
| ALFI | 🇱🇺 Luxembourg | EN | 5 |
| AMF | 🇫🇷 France | FR | 5 |
| CBI | 🇮🇪 Irlande | EN | 5 |
| CSSF | 🇱🇺 Luxembourg | FR | 5 |
| ESMA | 🇪🇺 Europe | EN | 5 |
| FINMA | 🇨🇭 Suisse | EN | 5 |

---

## 📂 Structure du Projet

```
AmundiGemScrapper/
├── config/                    # Configuration centralisée
│   ├── database.py           # Config MySQL
│   ├── settings.py           # Settings généraux
│   └── embeddings.py         # Config OpenAI
│
├── src/                       # Code source
│   ├── common/               # Utilitaires
│   │   └── driver_setup.py
│   ├── database/             # Gestion BDD
│   │   └── manager.py
│   ├── embeddings/           # Chunking + OpenAI
│   │   ├── chunker.py
│   │   └── openai_client.py
│   └── vectorstore/          # ChromaDB
│       └── chroma_manager.py
│
├── scripts/                   # Scripts d'administration
│   ├── run_scraping.py       # Scraping des sources
│   ├── run_ingestion.py      # JSON → MySQL
│   ├── run_vectorization.py  # MySQL → ChromaDB
│   ├── search_rag.py         # Recherche RAG
│   └── explore_chroma.py     # Explorer ChromaDB
│
├── scrapers/                  # Modules de scraping
│   └── [afg, afm, alfi, ...]
│
├── data/                      # Données générées
│   ├── json/                 # JSON des scrapers
│   └── chroma/               # Base vectorielle
│
└── docker-compose.yml         # MySQL + PHPMyAdmin
```

---

## 🚀 Installation

### 1. Prérequis
```bash
# Python 3.10+
python --version

# Docker Desktop (pour MySQL)
docker --version

# Google Chrome (pour Selenium)
```

### 2. Installation
```bash
# Cloner le repo
git clone [url]
cd AmundiGemScrapper

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# Dépendances
pip install -r requirements.txt
```

### 3. Configuration

**MySQL (Docker)**
```bash
docker-compose up -d
```

**Variables d'environnement**
```bash
# Créer un fichier .env à la racine
echo "OPENAI_API_KEY=sk-..." > .env
```

**Initialiser la base**
```bash
# La base est créée automatiquement au premier run
# Ou manuellement via PHPMyAdmin : http://localhost:8080
```

---

## 📋 Utilisation

### Pipeline Complet

```bash
# 1. Scraper les sources (génère les JSON)
python scripts/run_scraping.py

# 2. Ingérer les JSON dans MySQL
python scripts/run_ingestion.py

# 3. Vectoriser les articles (MySQL → ChromaDB)
python scripts/run_vectorization.py

# 4. Rechercher via RAG
python scripts/search_rag.py "What is ESMA's position on crypto?"
```

### Commandes Utiles

```bash
# Recherche simple
python scripts/search_rag.py "réglementation AMF cloud"

# Recherche avec filtre par source
python scripts/search_rag.py "Luxembourg regulations" --source CSSF

# Recherche avec plus de résultats
python scripts/search_rag.py "MiFID II" --n 10

# Explorer ChromaDB
python scripts/explore_chroma.py
```

---

## 💰 Coûts OpenAI

**Vectorisation initiale (45 articles) :**
- ~30K tokens
- Coût : **$0.0006** (~0.06 centimes)

**Recherche :**
- ~100 tokens par requête
- Coût : **$0.000002** par recherche (gratuit)

**Total mensuel estimé :** < $1

---

## 🔧 Maintenance

### Ajouter de nouvelles sources
1. Créer `scrapers/nouvelle_source/`
2. Implémenter `get_list.py` et `get_content.py`
3. Ajouter dans `config/settings.py` → `SOURCES_CONFIG`
4. Relancer le pipeline

### Réindexer ChromaDB
```bash
# Supprimer et recréer
python scripts/run_vectorization.py
# Répondre 'y' quand demandé
```


---

## 🎯 Roadmap

- [x] Scraping des 8 sources
- [x] Stockage MySQL
- [x] Vectorisation ChromaDB
- [x] Recherche RAG
- [ ] Interface Streamlit
- [ ] Génération de réponses (GPT-4)
- [ ] Scraping incrémental (nouveaux articles)
- [ ] Multi-tenancy (plusieurs utilisateurs)
- [ ] API REST

---

## 📊 Statistiques du Projet

- **45 articles** collectés
- **53 chunks** vectorisés
- **8 sources** réglementaires
- **2 langues** (FR/EN)
- **Coût total** : $0.0006

---

## 🐛 Dépannage

### MySQL inaccessible
```bash
docker ps  # Vérifier que le conteneur tourne
docker-compose up -d
```

### ChromaDB vide après vectorisation
```bash
# Vérifier que les fichiers existent
ls -la data/chroma/

# Relancer la vectorisation
python scripts/run_vectorization.py
```

### Clé OpenAI invalide
```bash
# Vérifier le .env
cat .env

# Exporter manuellement
export OPENAI_API_KEY="sk-..."
```
