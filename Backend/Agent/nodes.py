
from Backend.RAG.retriever import retrieve_policy_context
from Backend.LLM.model import get_llm
from Backend.LLM.model import get_llm, MODEL_NAME
from Backend.Tools.policy_search import search_policy
from Backend.Tools.eligibility import check_policy_eligibility
from Backend.Tools.actions import request_action


def retrieve_node(state):
    question = state["question"].strip()
    chat_history = state.get("chat_history", [])

    # Use recent conversation to clarify follow-up questions
    if chat_history:
        recent_messages = chat_history[-4:]

        history_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in recent_messages
        )

        retrieval_question = (
            f"Recent conversation:\n{history_text}\n\n"
            f"Current question: {question}\n\n"
            "Use the conversation only to understand the current "
            "question. Retrieve policy evidence that answers the "
            "current question."
        )
    else:
        retrieval_question = question

    context = retrieve_policy_context(retrieval_question)

    return {"context": context}


def answer_node(state):
    llm = get_llm()

    question = state["question"]
    context = state["context"]
    chat_history = state.get("chat_history", [])

    history_text = ""

    if chat_history:
        history_text = "\n\nConversation history:\n"

        for message in chat_history:
            history_text += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )

    system_instruction = """
You are PolicyPilot, an AI assistant that answers questions
about Airbnb policies.

Follow these rules carefully:

1. Answer using only the provided policy context.
2. Never invent policy rules, deadlines, amounts, or eligibility conditions.
3. Use conversation history to understand follow-up questions.
4. Conversation history provides context, not proof of policy facts.
5. Base policy claims only on the current retrieved policy context.
6. If the context is missing, irrelevant, unclear, or insufficient, say:
"I could not find enough information in the available policy documents."
7. Do not confirm eligibility unless the policy evidence and user's
circumstances sufficiently support the decision.
8. Ask a concise clarifying question when necessary details are missing.
9. Mention the source document when possible.
10. Never claim an action was completed without explicit tool confirmation.

Answer length:
- Short requested: 2-3 sentences when evidence allows.
- Detailed requested: explain relevant conditions in organized paragraphs
  or bullets.
- Otherwise: give a clear, concise answer.
"""

    user_input = f"""
Retrieved policy context:

{context}

{history_text}

Current question:
{question}
"""

    interaction = llm.interactions.create(
        model=MODEL_NAME,
        system_instruction=system_instruction,
        input=user_input,
        generation_config={
            "max_output_tokens": 500,
            "thinking_level": "low"
        }
    )

    return {
        "answer": interaction.output_text
    }

def policy_search_node(state):
    context = search_policy(state["question"])

    return {
        "context": context,
        "answer": context,
        "selected_tool": "policy_search"
    }


def eligibility_node(state):
    result = check_policy_eligibility(state["question"])

    return {
        "answer": result,
        "selected_tool": "eligibility"
    }



def action_node(state):
    question = state.get("question", "").strip()
    question_lower = question.lower()

    if "refund" in question_lower:
        action = "request_refund"
    elif "contact support" in question_lower:
        action = "contact_support"
    elif "cancel" in question_lower:
        action = "cancel_booking"
    else:
        return {
            "answer": (
                "Please clarify which supported action you want "
                "to request. No action has been performed."
            ),
            "selected_tool": "actions",
            "confirmed": False
        }

    result = request_action(
        action=action,
        details=question,
        confirmed=False
    )

    return {
        "answer": result,
        "selected_tool": "actions",
        "action_details": question,
        "confirmed": False
    }

