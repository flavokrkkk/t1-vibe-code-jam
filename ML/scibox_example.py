import os
from scibox_client import SciBoxClient
from scibox_config import DEFAULT_CHAT_MODEL, DEFAULT_CODER_MODEL, DEFAULT_EMBEDDING_MODEL
from embeddings_utils import get_embeddings, find_most_similar, cosine_similarity


def _get_api_key() -> str:
    """Получение API ключа из переменных окружения."""
    api_key = os.getenv("SCIBOX_API_KEY")
    if not api_key:
        raise ValueError("SCIBOX_API_KEY не установлен в переменных окружения")
    return api_key


def example_chat():
    """Пример использования универсальной чат-модели."""
    print("=== Пример: Универсальная чат-модель ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "/no_think Ты дружелюбный помощник"},
            {"role": "user", "content": "Расскажи анекдот"},
        ],
        model=DEFAULT_CHAT_MODEL,
        temperature=0.7,
        top_p=0.9,
        max_tokens=256,
    )
    
    print(f"Ответ: {response.choices[0].message.content}\n")


def example_coder():
    """Пример использования кодовой модели."""
    print("=== Пример: Кодовая модель ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "Ты помощник, который пишет и объясняет код"},
            {"role": "user", "content": "Напиши функцию на Python, которая проверяет палиндром"},
        ],
        model=DEFAULT_CODER_MODEL,
        temperature=0.2,
        top_p=0.8,
        max_tokens=400,
    )
    
    print(f"Ответ: {response.choices[0].message.content}\n")


def example_stream():
    """Пример потокового ответа."""
    print("=== Пример: Потоковый ответ ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    print("Ответ (поток): ", end="", flush=True)
    
    with client.chat_completion_stream(
        messages=[{"role": "user", "content": "Сделай краткое резюме книги Война и мир"}],
        model=DEFAULT_CHAT_MODEL,
        max_tokens=400,
    ) as stream:
        for event in stream:
            if event.type == "chunk":
                delta = getattr(event.chunk.choices[0].delta, "content", None)
                if delta:
                    print(delta, end="", flush=True)
            elif event.type == "message.completed":
                print("\n")


def example_embeddings_single():
    """Пример получения эмбеддинга для одного текста."""
    print("=== Пример: Эмбеддинг одного текста ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    response = client.embeddings(
        input_text="Напиши короткое стихотворение про осень",
        model=DEFAULT_EMBEDDING_MODEL,
    )
    
    embedding = response.data[0].embedding
    print(f"Размерность эмбеддинга: {len(embedding)}")
    print(f"Первые 5 значений: {embedding[:5]}\n")


def example_embeddings_batch():
    """Пример получения эмбеддингов для батча текстов."""
    print("=== Пример: Эмбеддинги батча текстов ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    texts = [
        "Что такое квантовая запутанность?",
        "Квантовая запутанность — это корреляция состояний частиц",
        "Python — язык программирования",
    ]
    
    response = client.embeddings(
        input_text=texts,
        model=DEFAULT_EMBEDDING_MODEL,
    )
    
    print(f"Количество эмбеддингов: {len(response.data)}")
    for i, item in enumerate(response.data):
        print(f"Текст {i+1}: {texts[i][:50]}...")
        print(f"  Размерность: {len(item.embedding)}\n")


def example_similarity_search():
    """Пример поиска похожих текстов."""
    print("=== Пример: Поиск похожих текстов ===\n")
    
    query = "Что такое квантовая физика?"
    
    candidates = [
        "Квантовая механика изучает поведение частиц на атомном уровне",
        "Python — это язык программирования высокого уровня",
        "Квантовая запутанность — это корреляция состояний частиц",
        "Машинное обучение использует алгоритмы для обучения моделей",
    ]
    
    results = find_most_similar(query, candidates, top_k=2)
    
    print(f"Запрос: {query}\n")
    print("Наиболее похожие тексты:")
    for text, score in results:
        print(f"  [{score:.4f}] {text}\n")


def example_similarity_comparison():
    """Пример сравнения схожести двух текстов."""
    print("=== Пример: Сравнение схожести ===\n")
    
    text1 = "Что такое квантовая запутанность?"
    text2 = "Квантовая запутанность — это корреляция состояний частиц"
    text3 = "Python — язык программирования"
    
    embeddings = get_embeddings([text1, text2, text3])
    
    sim_12 = cosine_similarity(embeddings[0], embeddings[1])
    sim_13 = cosine_similarity(embeddings[0], embeddings[2])
    
    print(f"Текст 1: {text1}")
    print(f"Текст 2: {text2}")
    print(f"Схожесть 1-2: {sim_12:.4f}\n")
    
    print(f"Текст 1: {text1}")
    print(f"Текст 3: {text3}")
    print(f"Схожесть 1-3: {sim_13:.4f}\n")


def example_list_models():
    """Пример получения списка доступных моделей."""
    print("=== Пример: Список моделей ===\n")
    
    client = SciBoxClient(api_key=_get_api_key())
    
    models = client.list_models()
    
    print("Доступные модели:")
    for model in models.data:
        print(f"  - {model.id}")


if __name__ == "__main__":
    try:
        example_chat()
        example_coder()
        example_embeddings_single()
        example_embeddings_batch()
        example_similarity_search()
        example_similarity_comparison()
        example_list_models()
        
        print("\n=== Потоковый пример (раскомментируйте для запуска) ===")
        print("# example_stream()")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        print("\nУбедитесь, что установлена переменная окружения SCIBOX_API_KEY")

