from sqlalchemy import create_engine, text

# Assure-toi que c'est le bon mot de passe (root ou vide)
DB_CONNECTION_STR = "mysql+pymysql://root:root@localhost:3306/amundi"

def add_column():
    print("⏳ Tentative de connexion...") # Ajout d'un print pour être sûr
    try:
        engine = create_engine(DB_CONNECTION_STR)
        with engine.connect() as conn:
            # On ajoute la colonne 'language'
            conn.execute(text("ALTER TABLE articles ADD COLUMN language VARCHAR(10) DEFAULT 'fr';"))
            print("✅ SUCCÈS : Colonne 'language' ajoutée !")
    except Exception as e:
        # Si l'erreur contient "Duplicate column", c'est que c'est déjà fait, donc c'est bon.
        if "Duplicate column" in str(e):
             print("✅ INFO : La colonne existe déjà, tout va bien.")
        else:
             print(f"❌ ERREUR : {e}")

# 👇 C'est cette partie qui manquait probablement 👇
if __name__ == "__main__":
    add_column()