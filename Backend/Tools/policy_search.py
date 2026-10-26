
from Backend.RAG.retriever import retrieve_policy_context


def search_policy(question: str) -> str:
    """Search available Airbnb policy documents."""
    if not question.strip():
        return "Please provide a policy question."

    context = retrieve_policy_context(question)

    if not context.strip():
        return "No relevant policy information was found."

    return context
