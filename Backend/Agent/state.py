from typing import TypedDict

class AgentState(TypedDict):
    question: str
    context: str
    answer: str
    selected_tool: str
    action_details: str
    confirmed: bool
    chat_history: list