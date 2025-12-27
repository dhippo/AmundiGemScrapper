"""
Chunking intelligent des articles en segments optimaux pour les embeddings
"""
import tiktoken
from typing import List, Dict
from config.embeddings import CHUNKING_CONFIG


def count_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """Compte le nombre de tokens dans un texte."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def split_text_into_chunks(text: str, metadata: Dict) -> List[Dict]:
    """
    Découpe un texte en chunks avec overlap.

    Args:
        text: Texte à découper
        metadata: Métadonnées de l'article (source, date, url, etc.)

    Returns:
        Liste de chunks avec leurs métadonnées
    """
    chunk_size = CHUNKING_CONFIG["chunk_size"]
    chunk_overlap = CHUNKING_CONFIG["chunk_overlap"]
    min_chunk_size = CHUNKING_CONFIG["min_chunk_size"]

    # Si le texte est court, retourner tel quel
    token_count = count_tokens(text)
    if token_count <= chunk_size:
        return [{
            "text": text,
            "metadata": {**metadata, "chunk_index": 0, "total_chunks": 1},
            "token_count": token_count
        }]

    # Découpage par paragraphes (plus naturel)
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_index = 0

    for paragraph in paragraphs:
        para_tokens = count_tokens(paragraph)

        # Si le paragraphe seul dépasse la limite, le forcer dans un chunk
        if para_tokens > chunk_size:
            if current_chunk:
                chunks.append({
                    "text": '\n\n'.join(current_chunk),
                    "metadata": {**metadata, "chunk_index": chunk_index},
                    "token_count": current_tokens
                })
                chunk_index += 1
                current_chunk = []
                current_tokens = 0

            # Découper le paragraphe en phrases
            sentences = paragraph.split('. ')
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)
                if current_tokens + sent_tokens > chunk_size and current_chunk:
                    chunks.append({
                        "text": '. '.join(current_chunk),
                        "metadata": {**metadata, "chunk_index": chunk_index},
                        "token_count": current_tokens
                    })
                    chunk_index += 1
                    current_chunk = [sentence]
                    current_tokens = sent_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens

        # Cas normal : accumuler les paragraphes
        elif current_tokens + para_tokens <= chunk_size:
            current_chunk.append(paragraph)
            current_tokens += para_tokens
        else:
            # Sauvegarder le chunk actuel
            if current_tokens >= min_chunk_size:
                chunks.append({
                    "text": '\n\n'.join(current_chunk),
                    "metadata": {**metadata, "chunk_index": chunk_index},
                    "token_count": current_tokens
                })
                chunk_index += 1

            # Commencer nouveau chunk avec overlap
            current_chunk = [paragraph]
            current_tokens = para_tokens

    # Ajouter le dernier chunk
    if current_chunk and current_tokens >= min_chunk_size:
        chunks.append({
            "text": '\n\n'.join(current_chunk),
            "metadata": {**metadata, "chunk_index": chunk_index},
            "token_count": current_tokens
        })
        chunk_index += 1

    # Ajouter le nombre total de chunks à chaque métadonnée
    for chunk in chunks:
        chunk["metadata"]["total_chunks"] = len(chunks)

    return chunks


def estimate_cost(total_tokens: int, model: str = "text-embedding-3-small") -> float:
    """
    Estime le coût des embeddings.

    Prix OpenAI (Dec 2024):
    - text-embedding-3-small: $0.02 / 1M tokens
    - text-embedding-3-large: $0.13 / 1M tokens
    """
    price_per_million = 0.02 if "small" in model else 0.13
    return (total_tokens / 1_000_000) * price_per_million