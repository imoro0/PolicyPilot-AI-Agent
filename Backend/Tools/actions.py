
def request_action(action: str, details: str, confirmed: bool = False) -> str:
    """Handle a safe demo action with explicit user confirmation."""

    allowed_actions = {
        "request_refund",
        "cancel_booking",
        "contact_support"
    }

    if action not in allowed_actions:
        return "This action is not supported."

    if not details.strip():
        return "Please provide details about the requested action."

    if not confirmed:
        return (
            f"Confirmation required for: {action}\n"
            f"Details: {details}\n"
            "No action has been performed. Please confirm before proceeding."
        )

    return (
        f"Demo action confirmed: {action}\n"
        f"Details: {details}\n"
        "This is a simulated action only. No real booking, refund, "
        "or support request has been changed or submitted."
    )
