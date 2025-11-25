SCIBOX_BASE_URL = "https://llm.t1v.scibox.tech/v1"
SCIBOX_BASE_URL_IP = "http://45.145.191.148:4000/v1"

MODELS = {
    "qwen3-32b-awq": {
        "name": "qwen3-32b-awq",
        "rps": 2,
        "type": "chat",
        "description": "Универсальная чат-модель",
    },
    "qwen3-coder-30b-a3b-instruct-fp8": {
        "name": "qwen3-coder-30b-a3b-instruct-fp8",
        "rps": 2,
        "type": "chat",
        "description": "Инструкционная кодовая модель",
    },
    "bge-m3": {
        "name": "bge-m3",
        "rps": 7,
        "type": "embedding",
        "description": "Эмбеддинг-модель для поиска и ранжирования",
    },
}

DEFAULT_CHAT_MODEL = "qwen3-32b-awq"
DEFAULT_CODER_MODEL = "qwen3-coder-30b-a3b-instruct-fp8"
DEFAULT_EMBEDDING_MODEL = "bge-m3"

