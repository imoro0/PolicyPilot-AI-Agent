
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def create_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def create_embeddings(chunks):
    model = create_embedding_model()

    texts = [chunk["text"] for chunk in chunks]
    vectors = model.embed_documents(texts)

    return [
        {**chunk, "embedding": vector}
        for chunk, vector in zip(chunks, vectors)
    ]
