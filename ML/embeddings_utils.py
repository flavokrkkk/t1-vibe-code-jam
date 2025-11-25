from __future__ import annotations

import os
import math
from scibox_client import SciBoxClient
from scibox_config import DEFAULT_EMBEDDING_MODEL


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Вычисление косинусного сходства между двумя векторами."""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def get_embeddings(
    texts: str | list[str],
    client: SciBoxClient | None = None,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    """Получение эмбеддингов для текста или списка текстов."""
    if client is None:
        api_key = os.getenv("SCIBOX_API_KEY")
        if not api_key:
            raise ValueError("SCIBOX_API_KEY не установлен в переменных окружения")
        client = SciBoxClient(api_key=api_key)
    
    response = client.embeddings(input_text=texts, model=model)
    
    if isinstance(texts, str):
        return [response.data[0].embedding]
    else:
        return [item.embedding for item in response.data]


def find_most_similar(
    query_text: str,
    candidate_texts: list[str],
    client: SciBoxClient | None = None,
    model: str = DEFAULT_EMBEDDING_MODEL,
    top_k: int = 1,
) -> list[tuple[str, float]]:
    """Поиск наиболее похожих текстов на запрос."""
    query_embedding = get_embeddings(query_text, client, model)[0]
    candidate_embeddings = get_embeddings(candidate_texts, client, model)
    
    similarities = [
        (text, cosine_similarity(query_embedding, emb))
        for text, emb in zip(candidate_texts, candidate_embeddings)
    ]
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]




def deduplicate_texts(
    texts: list[str],
    threshold: float = 0.95,
    client: SciBoxClient | None = None,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[str]:
    """Удаление дубликатов текстов на основе эмбеддингов."""
    if not texts:
        return []
    
    embeddings = get_embeddings(texts, client, model)
    unique_texts = [texts[0]]
    unique_embeddings = [embeddings[0]]
    
    for text, emb in zip(texts[1:], embeddings[1:]):
        is_duplicate = False
        for unique_emb in unique_embeddings:
            if cosine_similarity(emb, unique_emb) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_texts.append(text)
            unique_embeddings.append(emb)
    
    return unique_texts

