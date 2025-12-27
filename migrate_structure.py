"""
Script de migration pour restructurer le projet Amundi GEM Scraper
Lance ce script depuis la racine du projet : python migrate_structure.py
"""
import os
import shutil
from pathlib import Path


# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_step(msg):
    print(f"\n{Colors.BLUE}▶ {msg}{Colors.END}")


def print_success(msg):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg):
    print(f"  {Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg):
    print(f"  {Colors.RED}✗ {msg}{Colors.END}")


def create_directory(path):
    """Crée un dossier s'il n'existe pas."""
    Path(path).mkdir(parents=True, exist_ok=True)
    print_success(f"Créé : {path}")


def create_init_file(path):
    """Crée un fichier __init__.py vide."""
    init_path = os.path.join(path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("# Auto-generated __init__.py\n")
        print_success(f"Créé : {init_path}")


def backup_project():
    """Crée une copie de sauvegarde du projet actuel."""
    print_step("Création d'une sauvegarde...")

    backup_dir = "backup_before_migration"

    if os.path.exists(backup_dir):
        print_warning(f"Le dossier {backup_dir} existe déjà, suppression...")
        shutil.rmtree(backup_dir)

    # Copier certains fichiers critiques
    os.makedirs(backup_dir, exist_ok=True)

    files_to_backup = [
        "main.py",
        "init_db.py",
        "ingest_json.py",
        "add_language_column.py",
        "check_status.py"
    ]

    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print_success(f"Sauvegardé : {file}")

    print_success(f"Sauvegarde complète dans {backup_dir}/")


def create_new_structure():
    """Crée la nouvelle structure de dossiers."""
    print_step("Création de la nouvelle structure...")

    # Créer les dossiers principaux
    directories = [
        "config",
        "src",
        "src/database",
        "src/ingestion",
        "src/common",
        "src/scrapers",
        "scripts",
        "data",
        "data/json",
        "tests",
    ]

    for directory in directories:
        create_directory(directory)
        if directory.startswith("src") or directory == "config":
            create_init_file(directory)


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 60)
    print("🏗️  MIGRATION VERS UNE STRUCTURE PROFESSIONNELLE")
    print("=" * 60)

    # Vérification qu'on est bien à la racine
    if not os.path.exists("main.py") or not os.path.exists("scrapers"):
        print_error("Ce script doit être exécuté depuis la racine du projet !")
        print_error("Assure-toi d'être dans le dossier AmundiGemScrapper/")
        return

    print_warning("Ce script va restructurer ton projet.")
    print_warning("Une sauvegarde sera créée dans backup_before_migration/")

    response = input("\n👉 Continuer ? (y/n): ").lower().strip()

    if response != 'y':
        print("\n❌ Migration annulée.")
        return

    # Étape 1 : Sauvegarde
    backup_project()

    # Étape 2 : Créer la nouvelle structure
    create_new_structure()

    print("\n" + "=" * 60)
    print("✅ STRUCTURE DE BASE CRÉÉE !")
    print("=" * 60)

    print("\n📋 Prochaines étapes :")
    print("  1. Je vais te créer les fichiers de config")
    print("  2. On migrera ensuite les modules existants")
    print("  3. On créera les nouveaux scripts d'admin")

    print(f"\n💡 Sauvegarde disponible dans : {Colors.GREEN}backup_before_migration/{Colors.END}")
    print("\n🎯 Structure créée, prêt pour la suite !")


if __name__ == "__main__":
    main()