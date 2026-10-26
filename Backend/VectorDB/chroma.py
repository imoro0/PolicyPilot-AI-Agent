
from pathlib import Path
import chromadb

from Backend.RAG.loader import load_policy_pdfs
from Backend.RAG.splitter import split_policy_documents
from Backend.RAG.embeddings import create_embeddings
from Backend.RAG.embeddings import create_embedding_model


# Project ka root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ChromaDB ki permanent storage
CHROMA_DIR = PROJECT_ROOT / "Data" / "ChromaDB"

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name="airbnb_policies",
    metadata={"hnsw:space": "cosine"}
)


def get_policy_collection():
    return collection


def store_policy_chunks():
    # PDFs load karo
    documents = load_policy_pdfs()

    # Text ko chunks mein divide karo
    chunks = split_policy_documents(documents)

    # Har chunk ki embedding generate karo
    embedded_chunks = create_embeddings(chunks)

    # ChromaDB ke liye data prepare karo
    ids = [
        f"{chunk['source']}_{index}"
        for index, chunk in enumerate(embedded_chunks)
    ]

    texts = [
        chunk["text"]
        for chunk in embedded_chunks
    ]

    embeddings = [
        chunk["embedding"]
        for chunk in embedded_chunks
    ]

    metadatas = [
        {
            "source": chunk["source"],
            "category": chunk["category"]
        }
        for chunk in embedded_chunks
    ]

    # Records add ya update karo
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return collection.count()


from Backend.RAG.embeddings import create_embedding_model


def search_policies(question, n_results=3):
    model = create_embedding_model()
    question_vector = model.embed_query(question)

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        print(f"\nResult {i + 1}")
        print("Source:", metadata["source"])
        print("Category:", metadata["category"])
        print("Distance:", round(distance, 4))
        print("Text:", document[:500])




if __name__ == "__main__":
    results = collection.get(
        where={"source": "Privacy_Policy-English.pdf"},
        include=["metadatas", "documents"],
        limit=5
    )

    print("Privacy chunks found:", len(results["ids"]))

    for i, document in enumerate(results["documents"]):
        print(f"\nChunk {i + 1}")
        print("Category:", results["metadatas"][i]["category"])
        print("Text:", document[:500])


if __name__ == "__main__":
    search_policies(
        "What personal information does Airbnb collect about users?",
        n_results=5
    )
