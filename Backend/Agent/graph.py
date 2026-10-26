
from langgraph.graph import StateGraph, START, END

from Backend.Agent.state import AgentState
from Backend.Agent.nodes import (
    retrieve_node,
    answer_node,
    policy_search_node,
    eligibility_node,
    action_node
)
from Backend.Agent.router import route_question


def empty_question_node(state):
    return {
        "answer": "Please enter a question about Airbnb policies."
    }


def build_agent():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("empty", empty_question_node)
    graph.add_node("policy_search", policy_search_node)
    graph.add_node("eligibility", eligibility_node)
    graph.add_node("action", action_node)

    # Initial routing
    graph.add_conditional_edges(
        START,
        route_question,
        {
            "empty": "empty",
            "policy": "retrieve",
            "eligibility": "eligibility",
            "action": "action"
        }
    )

    # Normal RAG workflow
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    # Tool workflows
    graph.add_edge("eligibility", END)
    graph.add_edge("action", END)
    graph.add_edge("empty", END)

    return graph.compile()


agent = build_agent()




from Backend.Memory.conversation import (
    get_conversation_history,
    add_message
)


def run_agent(question: str, session_id: str = "default") -> str:
    question = question.strip()

    if not question:
        return "Please enter a question about Airbnb policies."

    chat_history = get_conversation_history(session_id)

    result = agent.invoke({
        "question": question,
        "context": "",
        "answer": "",
        "selected_tool": "",
        "action_details": "",
        "confirmed": False,
        "chat_history": chat_history
    })

    answer = result["answer"]

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return answer
