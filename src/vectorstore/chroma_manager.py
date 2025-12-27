"""
ChromaDB Manager - Gestion de la base vectorielle
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from config.embeddings import CHROMA_CONFIG


class ChromaManager:
    """Gestionnaire de la base vectorielle ChromaDB."""

    def __init__(self):
        """Initialise le client ChromaDB et la collection."""
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_CONFIG["persist_directory"]),
            settings=Settings(anonymized_telemetry=False)
        )

        # Créer ou récupérer la collection
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_CONFIG["collection_name"],
            metadata={"description": "Regulatory articles embeddings"}
        )

    def add_documents(self, texts, embeddings, metadatas, ids):
        """Ajoute des documents à la collection."""
        try:
            print(f"   📝 Tentative d'ajout de {len(ids)} documents...")
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            # Vérifier que c'est bien ajouté
            new_count = self.collection.count()
            print(f"   ✅ Ajout réussi ! Total: {new_count} documents")
        except Exception as e:
            print(f"   ❌ Erreur ChromaDB : {e}")
            raise

    def search(
            self,
            query_embedding: List[float],
            n_results: int = 5,
            where: Dict = None
    ) -> Dict:
        """
        Recherche les documents les plus similaires.

        Args:
            query_embedding: Vecteur d'embedding de la requête
            n_results: Nombre de résultats à retourner
            where: Filtres sur les métadonnées (ex: {"source": "ESMA"})

        Returns:
            Résultats de la recherche
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            print(f"❌ Erreur recherche : {e}")
            raise

    def count_documents(self) -> int:
        """Retourne le nombre de documents dans la collection."""
        return self.collection.count()

    def get_all_documents(self, limit: int = None) -> Dict:
        """Récupère tous les documents (ou un échantillon)."""
        count = self.count_documents()
        limit = limit or count

        return self.collection.get(
            limit=min(limit, count),
            include=["documents", "metadatas"]
        )

    def delete_collection(self):
        """Supprime complètement la collection."""
        self.client.delete_collection(CHROMA_CONFIG["collection_name"])
        print(f"   🗑️  Collection '{CHROMA_CONFIG['collection_name']}' supprimée")

    def reset_collection(self):
        """Réinitialise la collection (supprime et recrée)."""
        try:
            self.delete_collection()
        except:
            pass

        self.collection = self.client.get_or_create_collection(
            name=CHROMA_CONFIG["collection_name"],
            metadata={"description": "Regulatory articles embeddings"}
        )
        print(f"   🔄 Collection réinitialisée")