"""
Client OpenAI pour la génération d'embeddings
"""
import time
from typing import List
from openai import OpenAI
from config.embeddings import OPENAI_CONFIG, validate_openai_key


class OpenAIEmbeddings:
    """Client pour générer des embeddings via OpenAI API."""

    def __init__(self):
        validate_openai_key()
        self.client = OpenAI(api_key=OPENAI_CONFIG["api_key"])
        self.model = OPENAI_CONFIG["model"]
        self.total_tokens_used = 0

    def embed_text(self, text: str) -> List[float]:
        """
        Génère l'embedding d'un texte.

        Args:
            text: Texte à embedder

        Returns:
            Liste de float (vecteur d'embedding)
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            self.total_tokens_used += response.usage.total_tokens
            return response.data[0].embedding

        except Exception as e:
            print(f"❌ Erreur OpenAI : {e}")
            raise

    def embed_batch(self, texts: List[str], delay: float = 0.1) -> List[List[float]]:
        """
        Génère les embeddings d'un batch de textes.

        Args:
            texts: Liste de textes
            delay: Délai entre chaque appel (rate limiting)

        Returns:
            Liste d'embeddings
        """
        embeddings = []

        for i, text in enumerate(texts, 1):
            print(f"   Embedding {i}/{len(texts)}...", end='\r')

            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)

                # Rate limiting simple
                if i < len(texts):
                    time.sleep(delay)

            except Exception as e:
                print(f"\n   ⚠️  Erreur sur texte {i}: {e}")
                # Ajouter un vecteur vide en cas d'erreur
                embeddings.append([0.0] * OPENAI_CONFIG["dimensions"])

        print(f"\n   ✅ {len(embeddings)} embeddings générés")
        return embeddings

    def get_usage_stats(self) -> dict:
        """Retourne les statistiques d'utilisation."""
        from .chunker import estimate_cost

        return {
            "total_tokens": self.total_tokens_used,
            "estimated_cost_usd": estimate_cost(self.total_tokens_used, self.model),
            "model": self.model
        }