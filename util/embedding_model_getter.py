embedding_models: dict = {
    "cohere": "embed-multilingual-v3.0",
    "cohere-light": "embed-multilingual-light-v3.0",
}

def get_embedding_model(model_name: str) -> str:
    return embedding_models[model_name]