
from Backend.VectorDB.chroma import get_policy_collection
from Backend.RAG.embeddings import create_embedding_model


def retrieve_policy_context(question, n_results=10):
    if not question or not question.strip():
        return ""

    collection = get_policy_collection()
    embedding_model = create_embedding_model()
    question_embedding = embedding_model.embed_query(question)

    # Zyada candidates retrieve karo, phir relevant results select karo.
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=max(n_results, 10),
        include=["documents", "metadatas", "distances"]
    )

    question_lower = question.lower()

    if any(word in question_lower for word in [
        "privacy", "personal information", "personal data",
        "data collection", "collect my data", "information collect",
        "data do you collect", "use of my information"
    ]):
        preferred_sources = {"privacy_policy-english.pdf"}
        preferred_categories = {"privacy_policy", "privacy"}

    elif any(word in question_lower for word in [
        "refund", "refunded", "money back", "reimbursement"
    ]):
        preferred_sources = {
            "when_youll_get_your_refund.pdf",
            "rebooking_and_refund_policy_for_homes.pdf"
        }
        preferred_categories = {"refund_policy", "booking_and_refund_policy"}

    elif any(word in question_lower for word in [
        "cancel", "cancellation", "cancelled", "canceled"
    ]):
        preferred_sources = {
            "rebooking_and_refund_policy_for_homes.pdf"
        }
        preferred_categories = {
            "cancellation_policy", "booking_and_refund_policy"
        }

    else:
        preferred_sources = set()
        preferred_categories = set()

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    candidates = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        source = metadata.get("source", "").lower()
        category = metadata.get("category", "").lower()

        # Privacy questions mein privacy document ko priority do.
        preferred = (
            source in preferred_sources
            or category in preferred_categories
        )

        candidates.append({
            "document": document,
            "metadata": metadata,
            "distance": distance,
            "preferred": preferred
        })

    candidates.sort(
        key=lambda item: (
            not item["preferred"],
            item["distance"]
        )
    )

    # Sirf selected top results context mein bhejo.
    context_parts = []

    for item in candidates[:n_results]:
        metadata = item["metadata"]

        context_parts.append(
            f"Source: {metadata.get('source', 'Unknown')}\n"
            f"Category: {metadata.get('category', 'Unknown')}\n"
            f"Policy Text: {item['document']}"
        )

    return "\n\n".join(context_parts)
