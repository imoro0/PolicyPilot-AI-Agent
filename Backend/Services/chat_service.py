
from Backend.Agent.graph import run_agent


def chat_with_policy_agent(
    question: str,
    session_id: str = "default"
) -> str:
    """Send the question to the existing LangGraph agent."""

    question = question.strip()

    if not question:
        return "Please enter a question about Airbnb policies."

    return run_agent(
        question=question,
        session_id=session_id
    )
