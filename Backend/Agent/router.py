
def route_question(state):
    question = state.get("question", "").lower().strip()

    if not question:
        return "empty"

    action_keywords = [
        "request a refund",
        "cancel my booking",
        "cancel my reservation",
        "contact support",
        "submit a request"
    ]

    eligibility_keywords = [
        "am i eligible",
        "am i entitled",
        "do i qualify",
        "can i get a refund",
        "can i cancel"
    ]

    if any(keyword in question for keyword in action_keywords):
        return "action"

    if any(keyword in question for keyword in eligibility_keywords):
        return "eligibility"

    return "policy"
